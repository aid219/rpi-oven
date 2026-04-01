#!/usr/bin/env python3
"""
Touchscreen as Mouse - тачскрин работает как системная мышь
"""

import os
import time
import RPi.GPIO as GPIO
import smbus
import subprocess
import uinput

# Загружаем модули ядра
subprocess.run(['sudo', 'modprobe', 'i2c-dev'], capture_output=True)
subprocess.run(['sudo', 'modprobe', 'uinput'], capture_output=True)

# Конфигурация
TOUCH_ADDR = 0x38
RST_PIN = 27
WIDTH = 320
HEIGHT = 480

# Reset тачскрина - БЕЗ cleanup!
print('Reset touch...')
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.output(RST_PIN, GPIO.LOW)
time.sleep(0.1)
GPIO.output(RST_PIN, GPIO.HIGH)
time.sleep(0.2)
# НЕ cleanup() - держим RESET в HIGH!

# I2C
bus = smbus.SMBus(1)
print('I2C ready')

# Создаём виртуальную мышь через python-uinput
print('Creating virtual mouse...')

events = (uinput.BTN_LEFT, uinput.ABS_X, uinput.ABS_Y)
device = uinput.Device(events)
print('Virtual mouse created!')
print('Touch screen to move cursor')
print('Press Ctrl+C to exit')

last_x, last_y = -1, -1
last_pressed = False
touch_count = 0

try:
    while True:
        try:
            tc = bus.read_byte_data(TOUCH_ADDR, 0x02)
            if tc > 0:
                xh = bus.read_byte_data(TOUCH_ADDR, 0x03)
                xl = bus.read_byte_data(TOUCH_ADDR, 0x04)
                yh = bus.read_byte_data(TOUCH_ADDR, 0x05)
                yl = bus.read_byte_data(TOUCH_ADDR, 0x06)
                x = ((xh & 0x0F) << 8) | xl
                y = ((yh & 0x0F) << 8) | yl
                
                touch_count += 1
                print('Touch #{}: x={}, y={}'.format(touch_count, x, y))
                
                # Отправляем координаты только если изменились
                if x != last_x or y != last_y:
                    device.emit(uinput.ABS_X, x)
                    device.emit(uinput.ABS_Y, y)
                    last_x, last_y = x, y
                
                last_pressed = True
            else:
                if last_pressed:
                    last_pressed = False
        except Exception as e:
            print('Error:', e)
        time.sleep(0.02)

except KeyboardInterrupt:
    pass
finally:
    device.destroy()
    bus.close()
    # НЕ cleanup() - держим RESET в HIGH!
    print('\nStopped')

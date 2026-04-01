#!/usr/bin/env python3
"""
Simple Touch Test - проверка тачскрина
"""

import smbus
import RPi.GPIO as GPIO
import time

TOUCH_ADDR = 0x38
RST_PIN = 27

# Reset
GPIO.setmode(GPIO.BCM)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.output(RST_PIN, GPIO.LOW)
time.sleep(0.1)
GPIO.output(RST_PIN, GPIO.HIGH)
time.sleep(0.2)
# НЕ cleanup!

bus = smbus.SMBus(1)

print('Touch test - КОСАЙТЕСЬ ЭКРАНА!')
print('Ctrl+C для выхода')

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
                print('X={:3d} Y={:3d}'.format(x, y))
        except:
            pass
        time.sleep(0.05)
except KeyboardInterrupt:
    print('\nStop')
finally:
    bus.close()

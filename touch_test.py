#!/usr/bin/env python3
"""
Тест тачскрина - один скрипт reset + чтение
Запуск: sudo python3 touch_test.py
"""
import smbus
import RPi.GPIO as GPIO
import time

WIDTH = 320
HEIGHT = 480
TOUCH_ADDR = 0x38
RST_PIN = 27

print("=" * 40)
print("ТАЧСКРИН ТЕСТ")
print("=" * 40)

# Reset тачскрина
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.output(RST_PIN, GPIO.LOW)
time.sleep(0.1)
GPIO.output(RST_PIN, GPIO.HIGH)
time.sleep(0.1)
# НЕ делаем GPIO.cleanup() - держим RESET в HIGH!
print("Reset выполнен (RESET в HIGH)")

# I2C
bus = smbus.SMBus(1)
print("I2C открыт")

# Проверка что тачскрин найден
try:
    device_id = bus.read_byte(TOUCH_ADDR)
    print("Тачскрин найден: 0x{:02X}".format(TOUCH_ADDR))
except:
    print("ОШИБКА: Тачскрин не найден!")
    bus.close()
    exit(1)

print("\nКоснитесь экрана!")
print("Координаты:")
print("-" * 40)

try:
    while True:
        try:
            # Количество касаний
            tc = bus.read_byte_data(TOUCH_ADDR, 0x02)
            if tc > 0:
                # Координаты
                xh = bus.read_byte_data(TOUCH_ADDR, 0x03)
                xl = bus.read_byte_data(TOUCH_ADDR, 0x04)
                yh = bus.read_byte_data(TOUCH_ADDR, 0x05)
                yl = bus.read_byte_data(TOUCH_ADDR, 0x06)
                
                x = ((xh & 0x0F) << 8) | xl
                y = ((yh & 0x0F) << 8) | yl
                
                # БЕЗ инверсии!
                print("X={:3d} Y={:3d}".format(x, y))
        except Exception as e:
            print("Ошибка: {}".format(e))
        
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\n\nОстановлено")
finally:
    bus.close()
    print("Готово")

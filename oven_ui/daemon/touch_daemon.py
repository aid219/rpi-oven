#!/usr/bin/env python3
"""
Touch Daemon - на базе touch_reset_scan.py
"""

import smbus
import time
import RPi.GPIO as GPIO


TOUCH_ADDR = 0x38
RST_PIN = 27


# Reset - точно как в touch_reset_scan.py
GPIO.setmode(GPIO.BCM)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.output(RST_PIN, GPIO.LOW)
time.sleep(0.1)
GPIO.output(RST_PIN, GPIO.HIGH)
time.sleep(0.1)
# НЕ cleanup()!

bus = smbus.SMBus(1)

print('Touch daemon ready')

last_x, last_y, last_pressed = 0, 0, False

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
                print(x, "-", y)
        except OSError:
            # Ошибки I2C: устройство не отвечает, шина занята и т.п.
            print("I2C error, retrying...")
            time.sleep(0.1)
        except KeyboardInterrupt:
            # Это нужно, чтобы прерывание не проглотилось
            raise

except KeyboardInterrupt:
    print("\nStopping daemon...")

finally:
    # Освобождаем ресурсы: закрываем шину и сбрасываем GPIO
    bus.close()
    GPIO.cleanup()
    print("Resources released.")


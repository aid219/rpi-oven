#!/usr/bin/env python3
import smbus
import RPi.GPIO as GPIO
import time

print("=== TOUCH TEST ===")

# Reset
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.LOW)
time.sleep(0.1)
GPIO.output(27, GPIO.HIGH)
time.sleep(0.3)
GPIO.cleanup()

print("Reset done")

bus = smbus.SMBus(1)
print("Reading touch... Touch the screen!")

count = 0
while count < 200:
    try:
        tc = bus.read_byte_data(0x38, 0x02)
        if tc > 0:
            xh = bus.read_byte_data(0x38, 0x03)
            xl = bus.read_byte_data(0x38, 0x04)
            yh = bus.read_byte_data(0x38, 0x05)
            yl = bus.read_byte_data(0x38, 0x06)
            x = ((xh & 0x0F) << 8) | xl
            y = ((yh & 0x0F) << 8) | yl
            print(f"TOUCH! X={x}, Y={y}")
            count = 0
        else:
            count += 1
    except Exception as e:
        print(f"Error: {e}")
        count += 1
    time.sleep(0.05)

print("Done")

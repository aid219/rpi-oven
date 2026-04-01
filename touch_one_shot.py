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

# Scan
print("Scan I2C...")
for addr in range(0x03, 0x78):
    try:
        bus.read_byte(addr)
        print("Found: 0x{:02X}".format(addr))
    except:
        pass

print("Touch screen now!")
print("Coordinates:")

try:
    while True:
        try:
            tc = bus.read_byte_data(0x38, 0x02)
            if tc > 0:
                xh = bus.read_byte_data(0x38, 0x03)
                xl = bus.read_byte_data(0x38, 0x04)
                yh = bus.read_byte_data(0x38, 0x05)
                yl = bus.read_byte_data(0x38, 0x06)
                x = ((xh & 0x0F) << 8) | xl
                y = ((yh & 0x0F) << 8) | yl
                print("X={} Y={}".format(x, y))
        except:
            pass
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nStop")
finally:
    bus.close()

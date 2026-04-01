#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import smbus

RST_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.output(RST_PIN, GPIO.LOW)
time.sleep(0.1)
GPIO.output(RST_PIN, GPIO.HIGH)
time.sleep(0.3)
GPIO.cleanup()

print('Reset выполнен')

bus = smbus.SMBus(1)
print('Skanirovanie I2C...')
for addr in range(0x03, 0x78):
    try:
        bus.read_byte(addr)
        print(f'Found: 0x{addr:02X}')
    except:
        pass

print('Chtenie touch 0x38...')
for i in range(100):
    try:
        tc = bus.read_byte_data(0x38, 0x02)
        if tc > 0:
            xh = bus.read_byte_data(0x38, 0x03)
            xl = bus.read_byte_data(0x38, 0x04)
            yh = bus.read_byte_data(0x38, 0x05)
            yl = bus.read_byte_data(0x38, 0x06)
            x = ((xh & 0x0F) << 8) | xl
            y = ((yh & 0x0F) << 8) | yl
            print(f'TOUCH: x={x}, y={y}')
    except Exception as e:
        print(f'Error: {e}')
    time.sleep(0.05)

print('Touch screen test done')

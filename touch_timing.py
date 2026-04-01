#!/usr/bin/env python3
import smbus, RPi.GPIO as GPIO, time

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.LOW)
time.sleep(0.1)
GPIO.output(27, GPIO.HIGH)
time.sleep(0.1)

bus = smbus.SMBus(1)

print('Test 1 - сразу после reset:')
for i in range(20):
    try:
        tc = bus.read_byte_data(0x38, 0x02)
        if tc > 0:
            print('  TOUCH tc={}'.format(tc))
    except Exception as e:
        print('  Error:', e)
    time.sleep(0.05)

print('Test 2 - через 5 сек:')
time.sleep(5)
for i in range(20):
    try:
        tc = bus.read_byte_data(0x38, 0x02)
        if tc > 0:
            print('  TOUCH tc={}'.format(tc))
    except Exception as e:
        print('  Error:', e)
    time.sleep(0.05)

bus.close()
GPIO.cleanup()
print('Done')

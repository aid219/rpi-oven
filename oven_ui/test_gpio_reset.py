#!/usr/bin/env python3
import RPi.GPIO as GPIO
import smbus
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
print('GPIO 27 LOW')
GPIO.output(27, GPIO.LOW)
time.sleep(0.1)
print('GPIO 27 HIGH')
GPIO.output(27, GPIO.HIGH)
time.sleep(0.5)
print('Testing I2C...')

bus = smbus.SMBus(1)
for i in range(50):
    try:
        tc = bus.read_byte_data(0x38, 0x02)
        if tc > 0:
            print('TOUCH DETECTED!')
            break
    except:
        pass
    time.sleep(0.05)
else:
    print('No touch')

bus.close()
print('Done')

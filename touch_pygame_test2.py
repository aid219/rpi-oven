#!/usr/bin/env python3
import time
t0 = time.time()

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
print("pygame imported: {:.2f}s".format(time.time()-t0))

pygame.init()
print("pygame.init: {:.2f}s".format(time.time()-t0))

screen = pygame.Surface((320, 480))
print("Surface created: {:.2f}s".format(time.time()-t0))

import smbus, RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.LOW)
time.sleep(0.1)
GPIO.output(27, GPIO.HIGH)
time.sleep(0.1)

bus = smbus.SMBus(1)
print("I2C open: {:.2f}s".format(time.time()-t0))

print("\nTest touch AFTER pygame init:")
for i in range(40):
    try:
        tc = bus.read_byte_data(0x38, 0x02)
        if tc > 0:
            print("  TOUCH tc={}".format(tc))
    except Exception as e:
        print("  Error:", e)
    time.sleep(0.05)

bus.close()
GPIO.cleanup()
pygame.quit()
print("\nDone: {:.2f}s".format(time.time()-t0))

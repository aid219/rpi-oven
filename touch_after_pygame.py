#!/usr/bin/env python3
import time

print("Import pygame...")
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

print("pygame.init...")
pygame.init()
screen = pygame.Surface((320, 480))

print("Reset touch AFTER pygame...")
import smbus, RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.LOW)
time.sleep(0.1)
GPIO.output(27, GPIO.HIGH)
time.sleep(0.1)
# НЕ cleanup!

bus = smbus.SMBus(1)

print("Test touch:")
for i in range(40):
    try:
        tc = bus.read_byte_data(0x38, 0x02)
        if tc > 0:
            xh = bus.read_byte_data(0x38, 0x03)
            xl = bus.read_byte_data(0x38, 0x04)
            yh = bus.read_byte_data(0x38, 0x05)
            yl = bus.read_byte_data(0x38, 0x06)
            x = ((xh & 0x0F) << 8) | xl
            y = ((yh & 0x0F) << 8) | yl
            print("  TOUCH x={} y={}".format(x, y))
    except Exception as e:
        print("  Error:", e)
    time.sleep(0.05)

bus.close()
GPIO.cleanup()
pygame.quit()
print("Done")

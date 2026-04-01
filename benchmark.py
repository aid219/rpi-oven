#!/usr/bin/env python3
import time
t0 = time.time()

print("0. Start")

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
t1 = time.time()
print("1. os.environ: {:.3f}s".format(t1-t0))

import smbus
t2 = time.time()
print("2. smbus import: {:.3f}s".format(t2-t1))

import struct, fcntl, mmap
t3 = time.time()
print("3. struct/fcntl/mmap: {:.3f}s".format(t3-t2))

import RPi.GPIO as GPIO
t4 = time.time()
print("4. RPi.GPIO import: {:.3f}s".format(t4-t3))

import threading
t5 = time.time()
print("5. threading import: {:.3f}s".format(t5-t4))

import pygame
t6 = time.time()
print("6. pygame import: {:.3f}s".format(t6-t5))

print("Reset...")
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.LOW)
time.sleep(0.1)
GPIO.output(27, GPIO.HIGH)
time.sleep(0.1)
t7 = time.time()
print("7. Reset: {:.3f}s".format(t7-t6))

print("I2C...")
bus = smbus.SMBus(1)
t8 = time.time()
print("8. I2C open: {:.3f}s".format(t8-t7))

print("FB...")
fb = open('/dev/fb0', 'r+b')
fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
line_length = struct.unpack('I', fix_info[16:20])[0]
fb_mem = mmap.mmap(fb.fileno(), line_length * 480, prot=mmap.PROT_WRITE)
t9 = time.time()
print("9. Framebuffer: {:.3f}s".format(t9-t8))

print("pygame.init...")
pygame.init()
t10 = time.time()
print("10. pygame.init: {:.3f}s".format(t10-t9))

print("pygame.Surface...")
screen = pygame.Surface((320, 480))
t11 = time.time()
print("11. pygame.Surface: {:.3f}s".format(t11-t10))

print("\nTOTAL: {:.3f}s".format(t11-t0))
print("\nTest touch...")
for i in range(50):
    try:
        tc = bus.read_byte_data(0x38, 0x02)
        if tc > 0:
            print("  TOUCH!")
            break
    except:
        pass
    time.sleep(0.05)
else:
    print("  No touch detected")

bus.close()
fb_mem.close()
fb.close()
GPIO.cleanup()
pygame.quit()

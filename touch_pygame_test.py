#!/usr/bin/env python3
"""
Простой тест тачскрина - КОПИЯ ОРИГИНАЛА
Рисует крестик в точке касания
"""

import pygame
import smbus
import time
import struct
import fcntl
import mmap
import RPi.GPIO as GPIO

# Размеры
WIDTH = 320
HEIGHT = 480
TOUCH_ADDR = 0x38
RST_PIN = 27

# Reset тачскрина
print("Reset тачскрина...")
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.output(RST_PIN, GPIO.LOW)
time.sleep(0.1)
GPIO.output(RST_PIN, GPIO.HIGH)
time.sleep(0.2)
GPIO.cleanup()
print("Reset выполнен")

# Framebuffer - как в оригинале
fb = open('/dev/fb0', 'r+b')
fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
line_length = struct.unpack('I', fix_info[16:20])[0]
if line_length == 0:
    line_length = WIDTH * 2

fb_mem = mmap.mmap(fb.fileno(), line_length * HEIGHT, prot=mmap.PROT_WRITE)

# I2C
bus = smbus.SMBus(1)
print("I2C открыт")


def rgb565(r, g, b):
    """RGB565 little-endian - как в оригинале"""
    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return bytes([color & 0xFF, (color >> 8) & 0xFF])


def draw_filled_rect(x, y, w, h, color):
    """Как в оригинале"""
    color_bytes = rgb565(*color)
    line = color_bytes * w
    for iy in range(y, y + h):
        fb_mem.seek(iy * line_length + x * 2)
        fb_mem.write(line)


def draw_hline(x, y, w, color):
    """Как в оригинале"""
    color_bytes = rgb565(*color)
    line = color_bytes * w
    fb_mem.seek(y * line_length + x * 2)
    fb_mem.write(line)


def draw_vline(x, y, h, color):
    """Как в оригинале"""
    color_bytes = rgb565(*color)
    for iy in range(y, y + h):
        fb_mem.seek(iy * line_length + x * 2)
        fb_mem.write(color_bytes)


def draw_cross(cx, cy, color, size=20):
    """Рисует крестик"""
    # Горизонтальная линия
    draw_hline(max(0, cx-size), cy, min(size*2, WIDTH-cx+size), color)
    # Вертикальная линия
    draw_vline(cx, max(0, cy-size), min(size*2, HEIGHT-cy+size), color)


def get_touch():
    """Как в оригинале"""
    try:
        touch_count = bus.read_byte_data(TOUCH_ADDR, 0x02)
        if touch_count > 0:
            xh = bus.read_byte_data(TOUCH_ADDR, 0x03)
            xl = bus.read_byte_data(TOUCH_ADDR, 0x04)
            yh = bus.read_byte_data(TOUCH_ADDR, 0x05)
            yl = bus.read_byte_data(TOUCH_ADDR, 0x06)
            
            raw_x = ((xh & 0x0F) << 8) | xl
            raw_y = ((yh & 0x0F) << 8) | yl
            
            x = raw_x  # БЕЗ инверсии
            y = raw_y
            
            return (max(0, min(WIDTH-1, x)), max(0, min(HEIGHT-1, y)), raw_x, raw_y)
    except Exception as e:
        print(f"Ошибка: {e}")
        pass
    return None


# Очистка экрана
print("Очистка экрана...")
draw_filled_rect(0, 0, WIDTH, HEIGHT, (0, 0, 0))

last_x = 0
last_y = 0
was_touching = False

print("=== ТЕСТ ТАЧСКРИНА ===")
print("Коснитесь экрана - увидите красный крестик")
print("Координаты будут в консоли")

try:
    while True:
        touch = get_touch()
        
        if touch and not was_touching:
            x, y, raw_x, raw_y = touch
            last_x = x
            last_y = y
            
            # Очистка
            draw_filled_rect(0, 0, WIDTH, HEIGHT, (0, 0, 0))
            
            # Рисуем крестик
            draw_cross(x, y, (255, 0, 0))
            
            print(f"TOUCH: x={x}, y={y}, raw=({raw_x}, {raw_y})")
            
            was_touching = True
        elif not touch:
            was_touching = False
        
        time.sleep(0.05)

except KeyboardInterrupt:
    pass
finally:
    fb_mem.close()
    fb.close()
    bus.close()
    print("\nЗавершено!")

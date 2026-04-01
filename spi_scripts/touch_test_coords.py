#!/usr/bin/env python3
"""
Тест координат тачскрина - показывает крестик где касаешься
"""

import smbus
import time
import struct
import fcntl
import mmap

WIDTH = 320
HEIGHT = 480
TOUCH_ADDR = 0x38

def rgb565(r, g, b):
    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return bytes([color & 0xFF, (color >> 8) & 0xFF])

def draw_cross(fb_mem, line_length, cx, cy, color):
    """Нарисовать крестик"""
    color_bytes = rgb565(*color)
    # Горизонтальная линия
    for x in range(max(0, cx-20), min(WIDTH, cx+20)):
        for y in range(cy-2, cy+3):
            if 0 <= y < HEIGHT:
                fb_mem.seek(y * line_length + x * 2)
                fb_mem.write(color_bytes)
    # Вертикальная линия
    for y in range(max(0, cy-20), min(HEIGHT, cy+20)):
        for x in range(cx-2, cx+3):
            if 0 <= x < WIDTH:
                fb_mem.seek(y * line_length + x * 2)
                fb_mem.write(color_bytes)

def main():
    print("Коснись экрана - увидишь крестик в точке касания")
    print("Ctrl+C для выхода")
    
    fb = open('/dev/fb0', 'r+b')
    fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    if line_length == 0:
        line_length = WIDTH * 2
    
    fb_mem = mmap.mmap(fb.fileno(), line_length * HEIGHT, prot=mmap.PROT_WRITE)
    bus = smbus.SMBus(1)
    
    last_x, last_y = -1, -1
    
    try:
        while True:
            # Чёрный экран
            fb_mem.seek(0)
            fb_mem.write(b'\x00\x00' * WIDTH * HEIGHT)
            
            try:
                touch_count = bus.read_byte_data(TOUCH_ADDR, 0x02)
                if touch_count > 0:
                    xh = bus.read_byte_data(TOUCH_ADDR, 0x03)
                    xl = bus.read_byte_data(TOUCH_ADDR, 0x04)
                    yh = bus.read_byte_data(TOUCH_ADDR, 0x05)
                    yl = bus.read_byte_data(TOUCH_ADDR, 0x06)
                    
                    x = ((xh & 0x0F) << 8) | xl
                    y = ((yh & 0x0F) << 8) | yl
                    
                    # Пробуем разные варианты ориентации
                    # Вариант 1: инверсия обоих
                    x1 = WIDTH - x
                    y1 = HEIGHT - y
                    
                    # Рисуем крестики в разных вариантах
                    draw_cross(fb_mem, line_length, x1, y1, (255, 0, 0))  # Красный - инверсия
                    
                    print(f"Raw: {x},{y}  |  Inv: {x1},{y1}  ", end='\r')
                    
            except:
                pass
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        pass
    finally:
        fb_mem.close()
        fb.close()
        bus.close()

if __name__ == "__main__":
    main()

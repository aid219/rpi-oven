#!/usr/bin/env python3
"""
Тест вывода на ST7796U через framebuffer /dev/fb1
Прямой доступ к framebuffer без fbcon
"""

import os
import time
import struct
import fcntl
import mmap

FBIOGET_VSCREENINFO = 0x4600
FBIOGET_FSCREENINFO = 0x4602
FBIOPUT_VSCREENINFO = 0x4601

WIDTH = 320
HEIGHT = 480

print("Открываем /dev/fb1...")

with open('/dev/fb1', 'r+b') as fb:
    # Получаем фиксированную информацию
    fix_info = fcntl.ioctl(fb, FBIOGET_FSCREENINFO, bytes(128))
    smem_len_raw = struct.unpack('I', fix_info[4:8])[0]
    line_length = struct.unpack('I', fix_info[16:20])[0]
    
    print(f"smem_len_raw: {smem_len_raw}, line_length: {line_length}")
    
    # Вычисляем line_length для RGB565
    if line_length == 0:
        line_length = WIDTH * 2  # 2 байта на пиксель (RGB565)
    
    framebuffer_size = line_length * HEIGHT
    print(f"Framebuffer size: {framebuffer_size} байт")
    
    # Отображаем память framebuffer
    fb_mem = mmap.mmap(fb.fileno(), framebuffer_size, prot=mmap.PROT_WRITE)
    
    def rgb565(r, g, b):
        """Конвертировать RGB888 в RGB565"""
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    
    def fill_color(r, g, b):
        """Заполнить экран цветом"""
        color = struct.pack('>H', rgb565(r, g, b))  # Big-endian для RGB565
        frame = color * (WIDTH * HEIGHT)
        fb_mem.seek(0)
        fb_mem.write(frame)
    
    import mmap
    
    print("Заполняем красным...")
    fill_color(255, 0, 0)
    time.sleep(2)
    
    print("Заполняем зелёным...")
    fill_color(0, 255, 0)
    time.sleep(2)
    
    print("Заполняем синим...")
    fill_color(0, 0, 255)
    time.sleep(2)
    
    print("Заполняем белым...")
    fill_color(255, 255, 255)
    time.sleep(2)
    
    print("Заполняем чёрным...")
    fill_color(0, 0, 0)
    time.sleep(2)
    
    # Рисуем градиент
    print("Рисуем градиент...")
    for y in range(HEIGHT):
        offset = y * line_length
        r = int(255 * y / HEIGHT)
        b = int(255 * (HEIGHT - y) / HEIGHT)
        color = struct.pack('>H', rgb565(r, 0, b))
        row = color * WIDTH
        fb_mem.seek(offset)
        fb_mem.write(row)
    time.sleep(3)
    
    fb_mem.close()

print("Тест завершён!")

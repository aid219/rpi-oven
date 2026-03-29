#!/usr/bin/env python3
"""
Тест вывода на ST7796U через framebuffer /dev/fb1
"""

import fcntl
import struct

# IOCTL команды для framebuffer
FBIOGET_VSCREENINFO = 0x4600
FBIOGET_FSCREENINFO = 0x4602

# Открываем framebuffer
fb_path = '/dev/fb1'
print(f"Открываем {fb_path}...")

with open(fb_path, 'wb') as fb:
    # Получаем информацию о экране
    var_info = fcntl.ioctl(fb, FBIOGET_VSCREENINFO, bytes(160))
    
    # Парсим var_info (упрощённо)
    xres = struct.unpack('I', var_info[0:4])[0]
    yres = struct.unpack('I', var_info[4:8])[0]
    bits_per_pixel = struct.unpack('I', var_info[32:36])[0]
    
    print(f"Разрешение: {xres}x{yres}")
    print(f"Глубина цвета: {bits_per_pixel} бит")
    
    # Получаем фиксированную информацию
    fix_info = fcntl.ioctl(fb, FBIOGET_FSCREENINFO, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    smem_len = struct.unpack('I', fix_info[4:8])[0]
    
    print(f"Длина строки: {line_length} байт")
    print(f"Размер памяти: {smem_len} байт")
    
    # Заполняем экран белым цветом (RGB565: 0xFFFF)
    print("Заполняем экран белым...")
    white_pixel = bytes([0xFF, 0xFF])  # Белый в RGB565
    frame_size = line_length * yres
    white_frame = white_pixel * (frame_size // 2)
    fb.write(white_frame)
    fb.flush()
    
    print("Готово! Экран должен быть белым.")

print("Тест завершён")

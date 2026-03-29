#!/usr/bin/env python3
"""
Демонстрация на ST7796U - показывает анимацию на физическом дисплее
"""

import struct
import fcntl
import mmap
import time
import math

FBIOGET_FSCREENINFO = 0x4602

WIDTH = 320
HEIGHT = 480

def rgb565(r, g, b):
    """Конвертировать RGB888 в RGB565"""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

print("Открываем /dev/fb1...")

with open('/dev/fb1', 'r+b') as fb:
    fix_info = fcntl.ioctl(fb, FBIOGET_FSCREENINFO, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    if line_length == 0:
        line_length = WIDTH * 2
    
    fb_size = line_length * HEIGHT
    fb_mem = mmap.mmap(fb.fileno(), fb_size, prot=mmap.PROT_WRITE)
    
    def draw_pixel(x, y, r, g, b):
        """Нарисовать пиксель"""
        color = struct.pack('>H', rgb565(r, g, b))
        offset = y * line_length + x * 2
        fb_mem.seek(offset)
        fb_mem.write(color)
    
    def fill_screen(r, g, b):
        """Заполнить экран цветом"""
        color = struct.pack('>H', rgb565(r, g, b))
        frame = color * (WIDTH * HEIGHT)
        fb_mem.seek(0)
        fb_mem.write(frame)
    
    def draw_circle(cx, cy, radius, r, g, b):
        """Нарисовать круг"""
        for angle in range(0, 360, 2):
            x = cx + int(math.cos(math.radians(angle)) * radius)
            y = cy + int(math.sin(math.radians(angle)) * radius)
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                draw_pixel(x, y, r, g, b)
    
    def fill_circle(cx, cy, radius, r, g, b):
        """Заполнить круг"""
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x - cx)**2 + (y - cy)**2 <= radius**2:
                    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                        draw_pixel(x, y, r, g, b)
    
    def draw_text_demo():
        """Показать текст (простая имитация)"""
        fill_screen(0, 0, 0)
        # Рисуем рамку
        for i in range(10):
            fill_circle(WIDTH//2, HEIGHT//2 - 100, 60-i*2, 0, 100+i*10, 0)
        # Круг в центре
        fill_circle(WIDTH//2, HEIGHT//2, 40, 255, 255, 0)
        fill_circle(WIDTH//2, HEIGHT//2 + 80, 30, 0, 0, 255)
    
    print("\n=== ДЕМО НА ДИСПЛЕЕ ST7796U ===")
    print("Смотри на физический дисплей!\n")
    
    # 1. Белый экран
    print("1. Белый экран (3 сек)...")
    fill_screen(255, 255, 255)
    time.sleep(3)
    
    # 2. Красный
    print("2. Красный экран (2 сек)...")
    fill_screen(255, 0, 0)
    time.sleep(2)
    
    # 3. Зелёный
    print("3. Зелёный экран (2 сек)...")
    fill_screen(0, 255, 0)
    time.sleep(2)
    
    # 4. Синий
    print("4. Синий экран (2 сек)...")
    fill_screen(0, 0, 255)
    time.sleep(2)
    
    # 5. Градиент
    print("5. Вертикальный градиент (3 сек)...")
    for y in range(HEIGHT):
        r = int(255 * y / HEIGHT)
        b = int(255 * (HEIGHT - y) / HEIGHT)
        color = struct.pack('>H', rgb565(r, 0, b))
        row = color * WIDTH
        fb_mem.seek(y * line_length)
        fb_mem.write(row)
    time.sleep(3)
    
    # 6. Анимация круга
    print("6. Анимация прыгающего круга (10 сек)...")
    start_time = time.time()
    while time.time() - start_time < 10:
        t = time.time() - start_time
        # Прыгающий мяч
        ball_x = int(WIDTH/2 + math.sin(t * 2) * 100)
        ball_y = int(HEIGHT/2 + math.sin(t * 3) * 150)
        
        fill_screen(20, 20, 40)  # Тёмно-синий фон
        
        # Рисуем несколько кругов для эффекта
        fill_circle(ball_x, ball_y, 30, 255, 100, 0)
        fill_circle(ball_x, ball_y, 25, 255, 150, 0)
        fill_circle(ball_x, ball_y, 20, 255, 200, 50)
        
        # Рамка
        for i in range(5):
            draw_circle(WIDTH//2, HEIGHT//2, 150-i*5, 50, 50, 100)
    
    # 7. Радужные кольца
    print("7. Радужные кольца (5 сек)...")
    for frame in range(100):
        fill_screen(0, 0, 0)
        for i in range(10):
            radius = 30 + i * 25 + int(math.sin(time.time() * 3 + i) * 10)
            hue = (frame * 3 + i * 20) % 360
            r = int(128 + 127 * math.sin(math.radians(hue)))
            g = int(128 + 127 * math.sin(math.radians(hue + 120)))
            b = int(128 + 127 * math.sin(math.radians(hue + 240)))
            draw_circle(WIDTH//2, HEIGHT//2, radius, r, g, b)
        time.sleep(0.05)
    
    # 8. Финальный экран
    print("8. Финальный экран...")
    draw_text_demo()
    
    fb_mem.close()

print("\n=== ДЕМО ЗАВЕРШЕНО ===")
print("Дисплей должен показывать картинку с кругами")

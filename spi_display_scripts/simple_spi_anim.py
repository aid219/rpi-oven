#!/usr/bin/env python3
"""
Простая анимация на SPI дисплее через framebuffer
"""

import struct
import fcntl
import mmap
import time
import math

WIDTH = 320
HEIGHT = 480

def rgb565(r, g, b):
    """RGB888 to RGB565 little-endian"""
    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return bytes([color & 0xFF, (color >> 8) & 0xFF])

print("Открываем /dev/fb1...")

fb = open('/dev/fb1', 'r+b')
fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
line_length = struct.unpack('I', fix_info[16:20])[0]
if line_length == 0:
    line_length = WIDTH * 2

fb_size = line_length * HEIGHT
fb_mem = mmap.mmap(fb.fileno(), fb_size, prot=mmap.PROT_WRITE)

print(f"Framebuffer: {line_length} bytes/line, {fb_size} bytes total")

def clear(color_bytes):
    """Очистить экран цветом"""
    line = color_bytes * WIDTH
    for y in range(HEIGHT):
        fb_mem.seek(y * line_length)
        fb_mem.write(line)

def draw_circle(cx, cy, radius, color_bytes, fill=False):
    """Нарисовать круг"""
    if fill:
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x - cx)**2 + (y - cy)**2 <= radius**2:
                    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                        offset = y * line_length + x * 2
                        fb_mem.seek(offset)
                        fb_mem.write(color_bytes)
    else:
        # Простая окружность
        for angle in range(0, 360, 3):
            rad = math.radians(angle)
            x = int(cx + math.cos(rad) * radius)
            y = int(cy + math.sin(rad) * radius)
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                offset = y * line_length + x * 2
                fb_mem.seek(offset)
                fb_mem.write(color_bytes)

# Цвета
RED = rgb565(255, 0, 0)
GREEN = rgb565(0, 255, 0)
BLUE = rgb565(0, 0, 255)
YELLOW = rgb565(255, 255, 0)
WHITE = rgb565(255, 255, 255)
CYAN = rgb565(0, 255, 255)

print("\n=== ТЕСТ АНИМАЦИИ ===\n")

# Тест 1: Заполнение цветами
print("1. Тест цветов...")
for color, name in [(RED, 'RED'), (GREEN, 'GREEN'), (BLUE, 'BLUE'), (WHITE, 'WHITE')]:
    print(f"  {name}")
    clear(color)
    time.sleep(0.5)

# Тест 2: Анимация прыгающего мяча
print("\n2. Прыгающий мяч (20 сек)...")

ball_x = WIDTH // 2
ball_y = HEIGHT // 3
ball_vx = 5
ball_vy = 6
ball_radius = 20

start_time = time.time()
frame_count = 0

while time.time() - start_time < 20:
    frame_start = time.time()
    
    # Очистка (тёмно-синий фон)
    clear(rgb565(10, 10, 50))
    
    # Обновление позиции
    ball_x += ball_vx
    ball_y += ball_vy
    
    # Отскок от стен
    if ball_x - ball_radius <= 0 or ball_x + ball_radius >= WIDTH:
        ball_vx = -ball_vx
    if ball_y - ball_radius <= 0 or ball_y + ball_radius >= HEIGHT:
        ball_vy = -ball_vy
    
    # Рисуем мяч
    draw_circle(int(ball_x), int(ball_y), ball_radius, YELLOW, fill=True)
    draw_circle(int(ball_x), int(ball_y), ball_radius + 2, WHITE)
    
    # Счётчик FPS в углу (просто круги)
    fps = frame_count / (time.time() - start_time)
    for i in range(int(fps) % 10):
        draw_circle(30 + i * 25, 30, 10, CYAN, fill=True)
    
    frame_count += 1
    
    # Ограничение ~30 FPS
    elapsed = time.time() - frame_start
    if elapsed < 1/30:
        time.sleep(1/30 - elapsed)
    
    # Вывод FPS каждые 5 секунд
    if frame_count % 150 == 0:
        print(f"  FPS: {fps:.1f}")

print(f"\nИтого FPS: {frame_count / (time.time() - start_time):.1f}")

# Тест 3: Градиент
print("\n3. Градиент...")
for y in range(HEIGHT):
    r = int(255 * y / HEIGHT)
    b = int(255 * (HEIGHT - y) / HEIGHT)
    color = rgb565(r, 0, b)
    line = color * WIDTH
    fb_mem.seek(y * line_length)
    fb_mem.write(line)
time.sleep(2)

fb_mem.close()
fb.close()

print("\n=== ГОТОВО ===")

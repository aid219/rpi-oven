#!/usr/bin/env python3
"""Тест энкодера с выводом на экран"""
import time
import sys
import os
import signal
import pygame
import numpy as np

# Обработка Ctrl+C
running = True
def handler(sig, frame):
    global running
    running = False

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

# Импорт энкодера
sys.path.insert(0, '/home/qummy/oven_encoder')
from encoder_handler import Encoder

# Инициализация энкодера
encoder = Encoder(clk_pin=5, dt_pin=6)

# Инициализация pygame и framebuffer
pygame.init()
pygame.font.init()

# Размеры
width = 1024
height = 600
try:
    with open('/sys/class/graphics/fb0/virtual_size') as f:
        size = f.read().strip()
        width, height = map(int, size.split(','))
except:
    pass

try:
    with open('/sys/class/graphics/fb0/stride') as f:
        stride = int(f.read().strip())
except:
    stride = width * 2

# Открываем framebuffer
fb = open('/dev/fb0', 'r+b')
screen = pygame.Surface((width, height))
big_font = pygame.font.Font(None, 120)
font = pygame.font.Font(None, 36)

def write_to_fb():
    rgb_array = np.frombuffer(
        pygame.image.tostring(screen, 'RGB'), 
        dtype=np.uint8
    ).reshape((height, width, 3))
    
    r = rgb_array[:,:,0].astype(np.uint32)
    g = rgb_array[:,:,1].astype(np.uint32)
    b = rgb_array[:,:,2].astype(np.uint32)
    rgb565 = ((r >> 3) << 11 | (g >> 2) << 5 | (b >> 3)).astype(np.uint16)
    
    if stride > width * 2:
        padding = np.zeros((height, (stride - width * 2) // 2), dtype=np.uint16)
        rgb565 = np.hstack([rgb565, padding])
    
    fb.seek(0)
    fb.write(rgb565.tobytes())
    fb.flush()

# Главный цикл
last_value = 0
clock = pygame.time.Clock()

try:
    while running:
        # Получаем значение энкодера
        value = encoder.get_value()
        
        # Рисуем на экране
        screen.fill((30, 30, 50))
        
        # Рамка
        box_x, box_y = 362, 250
        box_width, box_height = 300, 150
        pygame.draw.rect(screen, (100, 100, 120), 
                        (box_x, box_y, box_width, box_height), border_radius=20)
        pygame.draw.rect(screen, (200, 200, 220), 
                        (box_x, box_y, box_width, box_height), 4, border_radius=20)
        
        # Число
        text = str(value)
        text_surf = big_font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(box_x + box_width // 2, box_y + box_height // 2))
        screen.blit(text_surf, text_rect)
        
        # Подсказка
        hint = font.render("← вращай энкодер →", True, (180, 180, 180))
        hint_rect = hint.get_rect(center=(width // 2, height - 80))
        screen.blit(hint, hint_rect)
        
        write_to_fb()
        clock.tick(60)
        
except KeyboardInterrupt:
    pass

encoder.stop()
fb.close()
pygame.quit()

#!/usr/bin/env python3
"""
Тест вывода на ST7796U через framebuffer с использованием pygame
"""

import os
import time

# Устанавливаем framebuffer перед импортом pygame
os.environ['SDL_FBDEV'] = '/dev/fb1'
os.environ['SDL_VIDEODRIVER'] = 'fbcon'

import pygame

WIDTH = 320
HEIGHT = 480

print("Инициализация pygame...")
pygame.init()

try:
    # Создаём поверхность
    screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 16)
    print(f"Создан дисплей: {WIDTH}x{HEIGHT}")
    
    # Заполняем белым
    print("Заполняем белым...")
    screen.fill((255, 255, 255))
    pygame.display.flip()
    time.sleep(2)
    
    # Заполняем красным
    print("Заполняем красным...")
    screen.fill((255, 0, 0))
    pygame.display.flip()
    time.sleep(2)
    
    # Заполняем зелёным
    print("Заполняем зелёным...")
    screen.fill((0, 255, 0))
    pygame.display.flip()
    time.sleep(2)
    
    # Заполняем синим
    print("Заполняем синим...")
    screen.fill((0, 0, 255))
    pygame.display.flip()
    time.sleep(2)
    
    # Рисуем градиент
    print("Рисуем градиент...")
    for y in range(HEIGHT):
        color = (int(255 * y / HEIGHT), 0, int(255 * (HEIGHT - y) / HEIGHT))
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))
    pygame.display.flip()
    time.sleep(3)
    
    # Пишем текст
    print("Пишем текст...")
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 48)
    text = font.render("Hello!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(5)
    
    print("Тест завершён!")
    
except Exception as e:
    print(f"Ошибка: {e}")
finally:
    pygame.quit()

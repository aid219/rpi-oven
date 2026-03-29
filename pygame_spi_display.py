#!/usr/bin/env python3
"""
Pygame на SPI дисплее ST7796U через framebuffer /dev/fb1
"""

import os
import sys

# Устанавливаем framebuffer ПЕРЕД импортом pygame
os.environ['SDL_VIDEODRIVER'] = 'directfb'
os.environ['SDL_DIRECTFB_FBDEV'] = '/dev/fb1'
os.environ['SDL_FBDEV'] = '/dev/fb1'
os.environ['SDL_AUDIODRIVER'] = 'dummy'  # Отключаем звук

import pygame
import time
import math

# Инициализация pygame
pygame.init()

# Параметры дисплея
WIDTH = 320
HEIGHT = 480

# Создаём окно на framebuffer
try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    print(f"Дисплей создан: {WIDTH}x{HEIGHT}")
except Exception as e:
    print(f"Ошибка создания дисплея: {e}")
    print("Пробуем без directfb...")
    os.environ['SDL_VIDEODRIVER'] = 'fbcon'
    os.environ['SDL_DIRECTFB_FBDEV'] = '/dev/fb1'
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 128, 0)

# Шрифты
pygame.font.init()
font_large = pygame.font.Font(None, 64)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

def draw_demo():
    """Демонстрация возможностей pygame на SPI дисплее"""
    
    running = True
    frame_count = 0
    start_time = time.time()
    
    # Параметры для анимации
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 3
    ball_radius = 25
    ball_speed_x = 3
    ball_speed_y = 4
    
    rect_x = 50
    rect_y = HEIGHT - 80
    rect_speed_x = 4
    rect_width = 80
    rect_height = 15
    
    rotation_angle = 0
    
    print("\n=== Pygame Demo на SPI дисплее ===")
    print("Нажми Ctrl+C для выхода\n")
    
    while running:
        try:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Очистка экрана (градиент)
            for y in range(HEIGHT):
                color_val = int(40 * y / HEIGHT)
                pygame.draw.line(screen, (color_val, color_val, color_val + 20), (0, y), (WIDTH, y))
            
            # Рисуем "солнце" (вращающийся круг с лучами)
            center_x = WIDTH // 2
            center_y = 100
            rotation_angle += 2
            
            # Лучи солнца
            for i in range(12):
                angle = math.radians(rotation_angle + i * 30)
                start_x = center_x + int(math.cos(angle) * 35)
                start_y = center_y + int(math.sin(angle) * 35)
                end_x = center_x + int(math.cos(angle) * 55)
                end_y = center_y + int(math.sin(angle) * 55)
                pygame.draw.line(screen, YELLOW, (start_x, start_y), (end_x, end_y), 3)
            
            # Центр солнца
            pygame.draw.circle(screen, YELLOW, (center_x, center_y), 30)
            pygame.draw.circle(screen, ORANGE, (center_x, center_y), 25, 3)
            
            # Прыгающий мяч
            ball_x += ball_speed_x
            ball_y += ball_speed_y
            
            # Отскок от стен
            if ball_x - ball_radius <= 0 or ball_x + ball_radius >= WIDTH:
                ball_speed_x = -ball_speed_x
            if ball_y - ball_radius <= 80 or ball_y + ball_radius >= HEIGHT - rect_height:
                ball_speed_y = -ball_speed_y
            
            # Ограничение по X
            ball_x = max(ball_radius, min(WIDTH - ball_radius, ball_x))
            
            # Рисуем мяч
            pygame.draw.circle(screen, RED, (int(ball_x), int(ball_y)), ball_radius)
            pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius, 3)
            
            # Ракетка (управление мышью или автоматическое)
            rect_x += rect_speed_x
            if rect_x <= 0 or rect_x + rect_width >= WIDTH:
                rect_speed_x = -rect_speed_x
            
            # Рисуем ракетку
            pygame.draw.rect(screen, GREEN, (rect_x, rect_y, rect_width, rect_height))
            pygame.draw.rect(screen, WHITE, (rect_x, rect_y, rect_width, rect_height), 2)
            
            # Счётчик FPS
            fps = clock.get_fps()
            fps_text = font_small.render(f"FPS: {fps:.1f}", True, WHITE)
            screen.blit(fps_text, (10, 10))
            
            # Время
            current_time = time.strftime("%H:%M:%S")
            time_text = font_small.render(current_time, True, CYAN)
            screen.blit(time_text, (WIDTH - 80, 10))
            
            # Обновление экрана
            pygame.display.flip()
            
            # Ограничение FPS
            clock.tick(60)
            
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed >= 1.0:
                print(f"FPS: {frame_count / elapsed:.1f}")
                frame_count = 0
                start_time = time.time()
                
        except KeyboardInterrupt:
            running = False
        except Exception as e:
            print(f"Ошибка: {e}")
            running = False
    
    return True

def draw_static_demo():
    """Статичная демонстрационная картинка"""
    
    # Фон
    screen.fill((20, 20, 40))
    
    # Заголовок
    title = font_large.render("ST7796U", True, YELLOW)
    title_rect = title.get_rect(center=(WIDTH // 2, 80))
    screen.blit(title, title_rect)
    
    # Подзаголовок
    subtitle = font_medium.render("320x480 SPI Display", True, WHITE)
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 130))
    screen.blit(subtitle, subtitle_rect)
    
    # Рисуем цветные полосы
    colors = [RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW, ORANGE, WHITE]
    strip_height = 25
    start_y = 180
    for i, color in enumerate(colors):
        pygame.draw.rect(screen, color, (10, start_y + i * strip_height, WIDTH - 20, strip_height - 2))
    
    # Текст
    info_text = font_small.render("Pygame + framebuffer", True, WHITE)
    info_rect = info_text.get_rect(center=(WIDTH // 2, 400))
    screen.blit(info_text, info_rect)
    
    # FPS тест
    fps_text = font_small.render("Press any key for animation", True, CYAN)
    fps_rect = fps_text.get_rect(center=(WIDTH // 2, 440))
    screen.blit(fps_text, fps_rect)
    
    pygame.display.flip()

def main():
    """Основная функция"""
    
    print("=" * 50)
    print("Pygame на SPI дисплее ST7796U")
    print("=" * 50)
    
    # Показываем статичную картинку 3 секунды
    draw_static_demo()
    time.sleep(3)
    
    # Запускаем анимацию
    draw_demo()
    
    # Очистка
    pygame.quit()
    print("\nЗавершено!")

if __name__ == "__main__":
    main()

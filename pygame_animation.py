#!/usr/bin/env python3
"""
Pygame анимация для Raspberry Pi
Вывод во фреймбуфер, плавные 30 FPS
"""

import os
import sys
import signal
import math
import pygame

# Настройки
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 480
TARGET_FPS = 30

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class BouncingBall:
    """Прыгающий мяч"""
    
    def __init__(self, x, y, radius, color, speed_x, speed_y):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
    
    def update(self, width, height):
        self.x += self.speed_x
        self.y += self.speed_y
        
        if self.x - self.radius < 0 or self.x + self.radius > width:
            self.speed_x = -self.speed_x
            self.x = max(self.radius, min(self.x, width - self.radius))
        
        if self.y - self.radius < 0 or self.y + self.radius > height:
            self.speed_y = -self.speed_y
            self.y = max(self.radius, min(self.y, height - self.radius))
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


def main():
    # Устанавливаем фреймбуфер
    os.environ['SDL_FBDEV'] = '/dev/fb0'
    os.environ['SDL_VIDEODRIVER'] = 'framebuffer'
    
    # Обработка Ctrl+C
    running = [True]  # используем список для изменения из closure
    
    def signal_handler(sig, frame):
        print("\nStopping...")
        running[0] = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Инициализация
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Animation Test")
    
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # Создаём мячи
    balls = [
        BouncingBall(60, 60, 25, (255, 0, 0), 3, 2),
        BouncingBall(160, 100, 30, (0, 255, 0), -2, 3),
        BouncingBall(260, 150, 20, (0, 0, 255), 4, -2),
        BouncingBall(100, 200, 22, (255, 255, 0), -3, -3),
        BouncingBall(200, 250, 28, (0, 255, 255), 2, -4),
    ]
    
    angle = 0
    frame_count = 0
    start_time = pygame.time.get_ticks()
    
    print("=" * 40)
    print("Pygame анимация запущена!")
    print(f"Экран: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"Цель FPS: {TARGET_FPS}")
    print("Нажми Ctrl+C для выхода")
    print("=" * 40)
    
    try:
        while running[0]:
            # События
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running[0] = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running[0] = False
            
            # Обновление
            for ball in balls:
                ball.update(SCREEN_WIDTH, SCREEN_HEIGHT)
            
            angle += 0.05
            
            # Отрисовка
            screen.fill(BLACK)
            
            # Сетка
            for x in range(0, SCREEN_WIDTH, 40):
                pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, 40):
                pygame.draw.line(screen, (40, 40, 40), (0, y), (SCREEN_WIDTH, y))
            
            # Мячи
            for ball in balls:
                ball.draw(screen)
            
            # FPS текст с меняющимся цветом
            elapsed = (pygame.time.get_ticks() - start_time) / 1000
            if elapsed > 0:
                current_fps = frame_count / elapsed if frame_count > 0 else 0
            
            r = int(127 + 127 * math.sin(angle))
            g = int(127 + 127 * math.sin(angle + 2))
            b = int(127 + 127 * math.sin(angle + 4))
            
            fps_text = f"FPS: {int(clock.get_fps())}"
            text_surface = font.render(fps_text, True, (r, g, b))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 30))
            screen.blit(text_surface, text_rect)
            
            # Инфо внизу
            info_font = pygame.font.Font(None, 24)
            info_text = f"Balls: {len(balls)} | Target: {TARGET_FPS} FPS"
            info_surface = info_font.render(info_text, True, WHITE)
            screen.blit(info_surface, (10, SCREEN_HEIGHT - 30))
            
            pygame.display.flip()
            clock.tick(TARGET_FPS)
            
            # Статистика каждые 60 кадров
            frame_count += 1
            if frame_count % 60 == 0:
                print(f"FPS: {clock.get_fps():.1f}")
    
    finally:
        pygame.quit()
        print("Pygame остановлен")


if __name__ == '__main__':
    main()

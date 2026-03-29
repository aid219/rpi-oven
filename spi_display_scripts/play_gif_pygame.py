#!/usr/bin/env python3
"""
Воспроизведение GIF на SPI дисплее через pygame
"""

import os
import sys
import time
from PIL import Image, ImageSequence
import pygame

# Параметры дисплея
WIDTH = 320
HEIGHT = 480

def main():
    # Путь к GIF файлу
    if len(sys.argv) > 1:
        gif_path = sys.argv[1]
    else:
        gif_path = '/tmp/1.gif'
    
    print(f"Загрузка {gif_path}...")
    
    # Открываем GIF
    img = Image.open(gif_path)
    print(f"Размер: {img.size}, Кадров: {img.n_frames}")
    
    # Инициализация pygame
    pygame.init()
    
    # Создаём окно на весь экран framebuffer
    os.environ['SDL_FBDEV'] = '/dev/fb1'
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    # Предзагрузка всех кадров
    frames = []
    durations = []
    
    for frame in ImageSequence.Iterator(img):
        # Конвертируем в RGB и масштабируем
        frame_rgb = frame.convert('RGB')
        frame_resized = frame_rgb.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        
        # Создаём поверхность pygame
        frame_surface = pygame.Surface((WIDTH, HEIGHT))
        
        # Копируем пиксели
        for y in range(HEIGHT):
            for x in range(WIDTH):
                r, g, b = frame_resized.getpixel((x, y))
                frame_surface.set_at((x, y), (r, g, b))
        
        frames.append(frame_surface)
        durations.append(frame.info.get('duration', 100))
    
    print(f"Загружено {len(frames)} кадров")
    
    # Воспроизведение
    clock = pygame.time.Clock()
    frame_index = 0
    total_frames = 0
    start_time = time.time()
    
    print("\n=== ВОСПРОИЗВЕДЕНИЕ ===")
    print("Нажми Ctrl+C или ESC для выхода\n")
    
    running = True
    while running:
        try:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Рисуем кадр
            screen.blit(frames[frame_index], (0, 0))
            pygame.display.flip()
            
            # Получаем длительность кадра
            duration = durations[frame_index] / 1000.0  # в секундах
            
            # Ждём
            time.sleep(duration)
            
            # Следующий кадр
            frame_index = (frame_index + 1) % len(frames)
            total_frames += 1
            
            # Статистика
            if total_frames % 100 == 0:
                elapsed = time.time() - start_time
                fps = total_frames / elapsed if elapsed > 0 else 0
                print(f"Кадров: {total_frames}, FPS: {fps:.1f}")
                
        except KeyboardInterrupt:
            running = False
    
    # Итоги
    elapsed = time.time() - start_time
    print(f"\nВсего кадров: {total_frames}")
    if elapsed > 0:
        print(f"Средний FPS: {total_frames / elapsed:.1f}")
    
    pygame.quit()
    print("Завершено!")

if __name__ == "__main__":
    main()

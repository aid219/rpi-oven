#!/usr/bin/env python3
"""
Воспроизведение GIF на SPI дисплее через pygame
Прямая запись в framebuffer через pygame.bufferproxy
"""

import os
import sys
import time
import struct
import fcntl
import mmap
from PIL import Image, ImageSequence
import pygame

WIDTH = 320
HEIGHT = 480

def main():
    # Путь к GIF файлу
    if len(sys.argv) > 1:
        gif_path = sys.argv[1]
    else:
        gif_path = '/tmp/2.gif'
    
    print(f"Загрузка {gif_path}...")
    
    # Открываем GIF
    img = Image.open(gif_path)
    print(f"Размер: {img.size}, Кадров: {img.n_frames}")
    
    # Открываем framebuffer напрямую
    fb = open('/dev/fb1', 'r+b')
    fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    if line_length == 0:
        line_length = WIDTH * 2
    
    fb_size = line_length * HEIGHT
    fb_mem = mmap.mmap(fb.fileno(), fb_size, prot=mmap.PROT_WRITE)
    print(f"Framebuffer: {line_length} bytes/line")
    
    # Предзагрузка всех кадров в поверхности pygame
    print("Преобразование кадров...")
    frames = []
    
    for i, frame in enumerate(ImageSequence.Iterator(img)):
        # Масштабируем и конвертируем в RGB
        frame_rgb = frame.convert('RGB')
        frame_resized = frame_rgb.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        
        # Создаём поверхность pygame
        surface = pygame.Surface((WIDTH, HEIGHT))
        
        # Копируем пиксели напрямую
        for y in range(HEIGHT):
            for x in range(WIDTH):
                r, g, b = frame_resized.getpixel((x, y))
                surface.set_at((x, y), (r, g, b))
        
        frames.append(surface)
        
        if i == 0:
            duration = frame.info.get('duration', 100)
            print(f"  Кадр 0: {duration}ms")
    
    print(f"Загружено {len(frames)} кадров")
    
    # Воспроизведение
    frame_index = 0
    total_frames = 0
    start_time = time.time()
    
    print("\n=== ВОСПРОИЗВЕДЕНИЕ ===")
    print("Нажми Ctrl+C или ESC для выхода\n")
    
    running = True
    while running:
        try:
            # Обработка событий pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Получаем текущий кадр
            frame = frames[frame_index]
            
            # Конвертируем в RGB565 байты
            frame_data = bytearray()
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    r, g, b = frame.get_at((x, y))[:3]
                    # RGB565 little-endian
                    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                    frame_data.extend([color & 0xFF, (color >> 8) & 0xFF])
            
            # Записываем в framebuffer построчно
            for y in range(HEIGHT):
                offset = y * line_length
                row_start = y * WIDTH * 2
                row_end = row_start + WIDTH * 2
                fb_mem.seek(offset)
                fb_mem.write(frame_data[row_start:row_end])
            
            # Получаем длительность кадра
            duration = img.info.get('duration', 100) / 1000.0
            
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
    
    fb_mem.close()
    fb.close()
    pygame.quit()
    print("Завершено!")

if __name__ == "__main__":
    pygame.init()
    main()

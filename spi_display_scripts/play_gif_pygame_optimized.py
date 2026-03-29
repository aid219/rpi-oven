#!/usr/bin/env python3
"""
Воспроизведение GIF на SPI дисплее через pygame - ОПТИМИЗИРОВАННАЯ ВЕРСИЯ
"""

import sys
import time
import struct
import fcntl
import mmap
from PIL import Image, ImageSequence
import pygame

WIDTH = 320
HEIGHT = 480

# Предварительно вычисляем таблицу RGB->RGB565 для скорости
def create_rgb565_table():
    """Создать таблицу конвертации RGB565 для скорости"""
    table = {}
    for r in range(256):
        for g in range(256):
            for b in range(256):
                # Попробуем инвертированный порядок
                color = ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | (r >> 3)
                table[(r, g, b)] = bytes([color & 0xFF, (color >> 8) & 0xFF])
    return table

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
    
    # Открываем framebuffer
    fb = open('/dev/fb1', 'r+b')
    fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    if line_length == 0:
        line_length = WIDTH * 2
    
    fb_size = line_length * HEIGHT
    fb_mem = mmap.mmap(fb.fileno(), fb_size, prot=mmap.PROT_WRITE)
    print(f"Framebuffer: {line_length} bytes/line")
    
    # Предзагрузка всех кадров - СРАЗУ В БАЙТЫ
    print("Преобразование кадров...")
    frames_bytes = []
    durations = []
    
    for i, frame in enumerate(ImageSequence.Iterator(img)):
        # Масштабируем
        frame_resized = frame.convert('RGB').resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        
        # Конвертируем в байты СРАЗУ
        frame_data = bytearray()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                r, g, b = frame_resized.getpixel((x, y))
                # RGB565 little-endian с инверсией RGB->BGR
                color = ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | (r >> 3)
                frame_data.extend([color & 0xFF, (color >> 8) & 0xFF])
        
        frames_bytes.append(bytes(frame_data))
        durations.append(frame.info.get('duration', 100) / 1000.0)
        
        if i == 0:
            print(f"  Кадр 0: {durations[0]*1000:.0f}ms")
    
    print(f"Загружено {len(frames_bytes)} кадров")
    
    # Воспроизведение
    frame_index = 0
    total_frames = 0
    start_time = time.time()
    
    print("\n=== ВОСПРОИЗВЕДЕНИЕ ===")
    print("Нажми Ctrl+C или ESC для выхода\n")
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        try:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Записываем кадр ВЕСЬ СРАЗУ (быстрее чем построчно)
            fb_mem.seek(0)
            fb_mem.write(frames_bytes[frame_index])
            
            # Ждём нужное время
            duration = durations[frame_index]
            elapsed = 0
            while elapsed < duration:
                clock.tick(60)  # Ограничение для стабильности
                elapsed = time.time() - start_time if total_frames == 0 else time.time() - frame_start
            
            # Следующий кадр
            frame_index = (frame_index + 1) % len(frames_bytes)
            total_frames += 1
            frame_start = time.time()
            
            # Статистика каждые 50 кадров
            if total_frames % 50 == 0:
                elapsed_total = time.time() - start_time
                fps = total_frames / elapsed_total if elapsed_total > 0 else 0
                print(f"Кадров: {total_frames}, FPS: {fps:.1f}")
                
        except KeyboardInterrupt:
            running = False
    
    # Итоги
    elapsed_total = time.time() - start_time
    print(f"\nВсего кадров: {total_frames}")
    if elapsed_total > 0:
        print(f"Средний FPS: {total_frames / elapsed_total:.1f}")
    
    fb_mem.close()
    fb.close()
    pygame.quit()
    print("Завершено!")

if __name__ == "__main__":
    pygame.init()
    main()

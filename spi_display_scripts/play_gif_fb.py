#!/usr/bin/env python3
"""
Воспроизведение GIF на SPI дисплее через прямой доступ к framebuffer
Оптимизированная версия с pygame.surface
"""

import struct
import fcntl
import mmap
import time
import sys
from PIL import Image, ImageSequence
import pygame

WIDTH = 320
HEIGHT = 480

def rgb565(r, g, b):
    """RGB888 to RGB565 little-endian"""
    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return bytes([color & 0xFF, (color >> 8) & 0xFF])

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
    
    # Открываем framebuffer
    fb = open('/dev/fb1', 'r+b')
    fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    if line_length == 0:
        line_length = WIDTH * 2
    
    fb_size = line_length * HEIGHT
    fb_mem = mmap.mmap(fb.fileno(), fb_size, prot=mmap.PROT_WRITE)
    print(f"Framebuffer: {line_length} bytes/line")
    
    # Предзагрузка всех кадров в формате RGB565
    print("Преобразование кадров...")
    frames = []
    
    for i, frame in enumerate(ImageSequence.Iterator(img)):
        # Масштабируем и конвертируем
        frame_rgb = frame.convert('RGB')
        frame_resized = frame_rgb.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        
        # Конвертируем в RGB565 байты
        frame_data = bytearray()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                r, g, b = frame_resized.getpixel((x, y))
                frame_data.extend(rgb565(r, g, b))
        
        frames.append(bytes(frame_data))
        duration = frame.info.get('duration', 100)
        
        if i == 0:
            print(f"  Кадр 0: {duration}ms")
    
    print(f"Загружено {len(frames)} кадров")
    
    # Воспроизведение
    frame_index = 0
    total_frames = 0
    start_time = time.time()
    
    print("\n=== ВОСПРОИЗВЕДЕНИЕ ===")
    print("Нажми Ctrl+C для выхода\n")
    
    try:
        while True:
            # Записываем кадр в framebuffer
            fb_mem.seek(0)
            fb_mem.write(frames[frame_index])
            
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
        elapsed = time.time() - start_time
        print(f"\nВсего кадров: {total_frames}")
        if elapsed > 0:
            print(f"Средний FPS: {total_frames / elapsed:.1f}")
    finally:
        fb_mem.close()
        fb.close()
    
    print("Завершено!")

if __name__ == "__main__":
    # Инициализация pygame для обработки событий (опционально)
    pygame.init()
    main()

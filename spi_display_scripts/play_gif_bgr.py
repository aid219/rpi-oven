#!/usr/bin/env python3
"""
Воспроизведение GIF на SPI дисплее - BGR порядок для правильных цветов
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

def rgb_to_rgb565(r, g, b):
    """RGB888 to RGB565 little-endian - МЕНЯЕМ КАНАЛЫ МЕСТАМИ"""
    # Пробуем BGR порядок вместо RGB
    color = ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | (r >> 3)
    return bytes([color & 0xFF, (color >> 8) & 0xFF])

def main():
    # Путь к GIF файлу
    if len(sys.argv) > 1:
        gif_path = sys.argv[1]
    else:
        gif_path = '/tmp/2.gif'
    
    print(f"Загрузка {gif_path}...")
    
    # Открываем GIF
    img = Image.open(gif_path)
    print(f"Режим: {img.mode}, Размер: {img.size}, Кадров: {img.n_frames}")
    
    # Открываем framebuffer
    fb = open('/dev/fb1', 'r+b')
    fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    if line_length == 0:
        line_length = WIDTH * 2
    
    fb_size = line_length * HEIGHT
    fb_mem = mmap.mmap(fb.fileno(), fb_size, prot=mmap.PROT_WRITE)
    print(f"Framebuffer: {line_length} bytes/line")
    
    # Предзагрузка всех кадров
    print("Преобразование кадров...")
    frames_bytes = []
    
    for i, frame in enumerate(ImageSequence.Iterator(img)):
        # Конвертируем в RGB правильно для палитровых GIF
        if frame.mode == 'P':
            frame_rgb = frame.convert('RGBA').convert('RGB')
        else:
            frame_rgb = frame.convert('RGB')
        
        # Масштабируем
        frame_resized = frame_rgb.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        
        # Конвертируем в байты - BGR порядок!
        frame_data = bytearray()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                r, g, b = frame_resized.getpixel((x, y))
                frame_data.extend(rgb_to_rgb565(r, g, b))
        
        frames_bytes.append(bytes(frame_data))
        
        if i == 0:
            duration = frame.info.get('duration', 100)
            print(f"  Кадр 0: {duration}ms")
    
    print(f"Загружено {len(frames_bytes)} кадров")
    
    # Воспроизведение
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
            
            # Записываем кадр ВЕСЬ СРАЗУ
            fb_mem.seek(0)
            fb_mem.write(frames_bytes[frame_index])
            
            # Ждём нужное время
            duration = img.info.get('duration', 100) / 1000.0
            time.sleep(duration)
            
            # Следующий кадр
            frame_index = (frame_index + 1) % len(frames_bytes)
            total_frames += 1
            
            # Статистика
            if total_frames % 50 == 0:
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

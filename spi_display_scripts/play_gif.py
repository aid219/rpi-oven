#!/usr/bin/env python3
"""
Воспроизведение GIF на SPI дисплее ST7796U через framebuffer
"""

import struct
import fcntl
import mmap
import time
from PIL import Image, ImageSequence

WIDTH = 320
HEIGHT = 480

def rgb565(r, g, b):
    """RGB888 to RGB565 little-endian"""
    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return bytes([color & 0xFF, (color >> 8) & 0xFF])

def open_framebuffer():
    """Открыть framebuffer"""
    fb = open('/dev/fb1', 'r+b')
    fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    if line_length == 0:
        line_length = WIDTH * 2
    
    fb_size = line_length * HEIGHT
    fb_mem = mmap.mmap(fb.fileno(), fb_size, prot=mmap.PROT_WRITE)
    return fb, fb_mem, line_length

def draw_frame(fb_mem, line_length, image):
    """Нарисовать кадр на весь экран"""
    # Масштабируем изображение до размера дисплея
    img_resized = image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    img_rgb = img_resized.convert('RGB')
    
    # Конвертируем в RGB565 и записываем по строкам
    pixels = img_rgb.load()
    for y in range(HEIGHT):
        line = b''
        for x in range(WIDTH):
            r, g, b = pixels[x, y]
            line += rgb565(r, g, b)
        fb_mem.seek(y * line_length)
        fb_mem.write(line)

def play_gif(gif_path):
    """Воспроизвести GIF в бесконечном цикле"""
    print(f"Открываю {gif_path}...")
    
    img = Image.open(gif_path)
    print(f"Размер: {img.size}")
    print(f"Формат: {img.format}")
    print(f"Режим: {img.mode}")
    
    # Получаем длительность кадров
    if hasattr(img, 'n_frames'):
        n_frames = img.n_frames
        print(f"Количество кадров: {n_frames}")
    else:
        n_frames = 1
    
    fb, fb_mem, line_length = open_framebuffer()
    print(f"Framebuffer: {line_length} bytes/line")
    
    frame_count = 0
    total_time = 0
    
    try:
        print("\n=== ВОСПРОИЗВЕДЕНИЕ GIF ===")
        print("Нажми Ctrl+C для остановки\n")
        
        while True:
            for frame in ImageSequence.Iterator(img):
                frame_start = time.time()
                
                # Получаем длительность кадра (в мс)
                duration = frame.info.get('duration', 100)
                
                # Рисуем кадр
                draw_frame(fb_mem, line_length, frame)
                
                frame_time = time.time() - frame_start
                total_time += frame_time
                frame_count += 1
                
                # Ждём нужное время
                if duration > 0:
                    sleep_time = duration / 1000.0 - frame_time
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                
                # Статистика каждые 100 кадров
                if frame_count % 100 == 0:
                    fps = frame_count / total_time if total_time > 0 else 0
                    print(f"Кадров: {frame_count}, FPS: {fps:.1f}")
                    
    except KeyboardInterrupt:
        print(f"\n\nОстановлено пользователем")
        print(f"Всего кадров показано: {frame_count}")
        if total_time > 0:
            print(f"Средний FPS: {frame_count / total_time:.1f}")
    finally:
        fb_mem.close()
        fb.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        gif_file = sys.argv[1]
    else:
        # По умолчанию ищем 1.gif в текущей директории
        gif_file = '/tmp/1.gif'
    
    play_gif(gif_file)

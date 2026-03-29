#!/usr/bin/env python3
"""
Воспроизведение видео на SPI дисплее через pygame + opencv
"""

import sys
import time
import struct
import fcntl
import mmap
import cv2
import pygame

WIDTH = 320
HEIGHT = 480

def main():
    # Путь к видео файлу
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = '/tmp/1.mp4'
    
    print(f"Загрузка {video_path}...")
    
    # Открываем видео через OpenCV
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Ошибка открытия видео: {video_path}")
        return
    
    # Получаем параметры видео
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Видео: {width}x{height}, {fps:.1f} FPS, {total_frames} кадров")
    
    # Открываем framebuffer (SPI дисплей = fb0)
    fb = open('/dev/fb0', 'r+b')
    fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    if line_length == 0:
        line_length = WIDTH * 2
    
    fb_size = line_length * HEIGHT
    fb_mem = mmap.mmap(fb.fileno(), fb_size, prot=mmap.PROT_WRITE)
    print(f"Framebuffer: {line_length} bytes/line")
    
    print("\n=== ВОСПРОИЗВЕДЕНИЕ ===")
    print("Нажми Ctrl+C или ESC для выхода\n")
    
    running = True
    frame_count = 0
    start_time = time.time()
    
    # Задержка между кадрами
    frame_delay = 1.0 / fps if fps > 0 else 1.0/30
    
    while running:
        try:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Читаем кадр из видео
            ret, frame = cap.read()
            
            if not ret:
                # Видео закончилось - начинаем сначала
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    break
            
            # Конвертируем BGR -> RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Масштабируем к размеру дисплея
            frame_resized = cv2.resize(frame_rgb, (WIDTH, HEIGHT), interpolation=cv2.INTER_LINEAR)
            
            # Конвертируем в RGB565 байты
            frame_data = bytearray()
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    r, g, b = frame_resized[y, x]
                    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                    frame_data.extend([color & 0xFF, (color >> 8) & 0xFF])
            
            # Записываем в framebuffer
            fb_mem.seek(0)
            fb_mem.write(frame_data)
            
            # Ждём нужное время для поддержания FPS
            elapsed = time.time() - start_time
            expected_time = frame_count * frame_delay
            if expected_time > elapsed:
                time.sleep(expected_time - elapsed)
            
            frame_count += 1
            
            # Статистика каждые 100 кадров
            if frame_count % 100 == 0:
                elapsed_total = time.time() - start_time
                actual_fps = frame_count / elapsed_total if elapsed_total > 0 else 0
                print(f"Кадров: {frame_count}/{total_frames}, FPS: {actual_fps:.1f}")
                
        except KeyboardInterrupt:
            running = False
    
    # Итоги
    elapsed_total = time.time() - start_time
    print(f"\nВсего кадров: {frame_count}")
    if elapsed_total > 0:
        print(f"Средний FPS: {frame_count / elapsed_total:.1f}")
    
    cap.release()
    fb_mem.close()
    fb.close()
    pygame.quit()
    print("Завершено!")

if __name__ == "__main__":
    pygame.init()
    main()

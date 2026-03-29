#!/usr/bin/env python3
"""
Воспроизведение видео на SPI дисплее через opencv (без pygame)
"""

import sys
import time
import struct
import fcntl
import mmap
import cv2
import signal

WIDTH = 320
HEIGHT = 480

running = True

def signal_handler(sig, frame):
    global running
    running = False
    print("\nОстановка...")

def main():
    global running
    
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
    print("Нажми Ctrl+C для остановки\n")
    
    frame_count = 0
    start_time = time.time()
    
    # Задержка между кадрами
    frame_delay = 1.0 / fps if fps > 0 else 1.0/30
    
    while running:
        try:
            # Читаем кадр из видео
            ret, frame = cap.read()
            
            if not ret:
                # Видео закончилось - начинаем сначала
                print("Видео закончилось, начинаем сначала...")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    break
            
            # OpenCV читает в BGR, конвертируем в RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Масштабируем к размеру дисплея
            frame_resized = cv2.resize(frame_rgb, (WIDTH, HEIGHT), interpolation=cv2.INTER_LINEAR)
            
            # Конвертируем в RGB565 байты - БЫСТРЫЙ СПОСОБ через numpy
            import numpy as np
            
            # RGB565 little-endian для panel-mipi-dbi
            r = frame_resized[:,:,0].astype(np.uint16)
            g = frame_resized[:,:,1].astype(np.uint16)
            b = frame_resized[:,:,2].astype(np.uint16)
            
            # Формула RGB565: RRRRRGGGGGGBBBBB
            rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
            rgb565 = rgb565.astype('<u2')  # little-endian
            
            # Записываем в framebuffer
            fb_mem.seek(0)
            fb_mem.write(rgb565.tobytes())
            
            frame_count += 1
            
            # Статистика каждые 100 кадров
            if frame_count % 100 == 0:
                elapsed = time.time() - start_time
                actual_fps = frame_count / elapsed if elapsed > 0 else 0
                print(f"Кадров: {frame_count}/{total_frames}, FPS: {actual_fps:.1f}")
            
        except KeyboardInterrupt:
            running = False
        except Exception as e:
            print(f"Ошибка: {e}")
            running = False
    
    # Итоги
    elapsed = time.time() - start_time
    print(f"\nВсего кадров: {frame_count}")
    if elapsed > 0:
        print(f"Средний FPS: {frame_count / elapsed:.1f}")
    
    cap.release()
    fb_mem.close()
    fb.close()
    print("Завершено!")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    main()

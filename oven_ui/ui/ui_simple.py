#!/usr/bin/env python3
"""
Oven UI - 1 кнопка для теста, БЕЗ принтов в цикле
"""

import os
import time
import struct
import fcntl
import mmap
import pygame

WIDTH = 320
HEIGHT = 480
COORDS_FILE = '/tmp/touch_coords.dat'

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

def rgb565(r, g, b):
    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return bytes([color & 0xFF, (color >> 8) & 0xFF])

def fb_update(screen, fb_mem, line_length):
    surface_data = pygame.surfarray.array3d(screen)
    fb_data = bytearray()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = surface_data[x][y]
            fb_data.extend(rgb565(r, g, b))
    fb_mem.seek(0)
    fb_mem.write(fb_data)

def read_touch():
    try:
        if os.path.exists(COORDS_FILE):
            with open(COORDS_FILE, 'r') as f:
                line = f.read().strip()
                if line:
                    parts = line.split(',')
                    if len(parts) == 3:
                        return (int(parts[0]), int(parts[1]), int(parts[2]) == 1)
    except:
        pass
    return (0, 0, False)

def main():
    # Ждём демон
    for i in range(50):
        if os.path.exists(COORDS_FILE):
            break
        time.sleep(0.1)
    else:
        print('No touch daemon!')
        return
    
    pygame.init()
    screen = pygame.Surface((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)
    
    fb = open('/dev/fb0', 'r+b')
    fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    if line_length == 0:
        line_length = WIDTH * 2
    fb_mem = mmap.mmap(fb.fileno(), line_length * HEIGHT, prot=mmap.PROT_WRITE)
    
    # 1 кнопка для теста
    btn_rect = pygame.Rect(40, 200, 240, 80)
    btn_state = False
    btn_anim = 0
    
    print('Ready!')
    
    running = True
    last_pressed = False
    
    try:
        while running:
            dt = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
            
            # Тачскрин
            x, y, pressed = read_touch()
            
            if pressed and not last_pressed:
                if btn_rect.collidepoint(x, y):
                    btn_state = not btn_state
            
            last_pressed = pressed
            
            # Анимация
            target = 1.0 if btn_state else 0.0
            btn_anim += (target - btn_anim) * 10 * dt
            btn_anim = max(0, min(1, btn_anim))
            
            # Отрисовка
            screen.fill((20, 20, 40))
            
            # Кнопка
            r = int(50 + 200 * btn_anim)
            g = int(50 + 100 * btn_anim)
            b = int(70 + 80 * btn_anim)
            color = (r, g, b)
            
            pygame.draw.rect(screen, color, btn_rect, border_radius=20)
            pygame.draw.rect(screen, (255, 255, 255), btn_rect, width=3, border_radius=20)
            
            # Текст
            text = font.render('TEST', True, (255, 255, 255))
            text_x = btn_rect.centerx - text.get_width() // 2
            text_y = btn_rect.centery - text.get_height() // 2
            screen.blit(text, (text_x, text_y))
            
            # Индикатор
            ind_color = (0, 255, 100) if btn_state else (80, 80, 80)
            pygame.draw.circle(screen, ind_color, (btn_rect.right - 40, btn_rect.centery), 10)
            
            fb_update(screen, fb_mem, line_length)
    
    except KeyboardInterrupt:
        pass
    finally:
        fb_mem.close()
        fb.close()
        pygame.quit()

if __name__ == '__main__':
    main()

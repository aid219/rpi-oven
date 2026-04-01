#!/usr/bin/env python3
"""
Oven UI - БЫСТРАЯ отрисовка БЕЗ array3d
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
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def fb_update_fast(screen, fb_mem, line_length):
    """Быстрая запись - используем tostring вместо array3d"""
    # Получаем сырые RGB данные
    rgb_data = pygame.image.tostring(screen, 'RGB')
    
    # Конвертируем в RGB565
    fb_data = bytearray(WIDTH * 2)
    for y in range(HEIGHT):
        offset = y * WIDTH * 3
        fb_offset = y * line_length
        for x in range(WIDTH):
            r = rgb_data[offset + x*3]
            g = rgb_data[offset + x*3 + 1]
            b = rgb_data[offset + x*3 + 2]
            c = rgb565(r, g, b)
            fb_data[x*2] = c & 0xFF
            fb_data[x*2 + 1] = (c >> 8) & 0xFF
        fb_mem.seek(fb_offset)
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
    print('Waiting for daemon...')
    for i in range(50):
        if os.path.exists(COORDS_FILE):
            break
        time.sleep(0.1)
    else:
        print('ERROR: No daemon!')
        return
    
    print('Starting pygame...')
    pygame.init()
    screen = pygame.Surface((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font_large = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 32)
    
    fb = open('/dev/fb0', 'r+b')
    fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    if line_length == 0:
        line_length = WIDTH * 2
    fb_mem = mmap.mmap(fb.fileno(), line_length * HEIGHT, prot=mmap.PROT_WRITE)
    
    btn_rect = pygame.Rect(40, 200, 240, 80)
    btn_state = False
    btn_anim = 0
    
    print('Ready! Touch button, ESC to exit')
    
    running = True
    last_pressed = False
    last_x, last_y = 0, 0
    
    try:
        while running:
            dt = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            x, y, pressed = read_touch()
            
            if pressed:
                if x != last_x or y != last_y:
                    print('Touch: {},{}'.format(x, y))
                    last_x, last_y = x, y
                
                if not last_pressed and btn_rect.collidepoint(x, y):
                    btn_state = not btn_state
                    print('  BUTTON -> {}'.format('ON' if btn_state else 'OFF'))
            
            last_pressed = pressed
            
            btn_anim += ((1.0 if btn_state else 0.0) - btn_anim) * 10 * dt
            
            screen.fill((20, 20, 40))
            
            title = font_small.render('Touch Test', True, (255, 255, 255))
            screen.blit(title, (10, 10))
            
            r = int(max(0, min(255, 50 + 200 * btn_anim)))
            g = int(max(0, min(255, 50 + 100 * btn_anim)))
            b = int(max(0, min(255, 70 + 80 * btn_anim)))
            
            pygame.draw.rect(screen, (r, g, b), btn_rect)
            pygame.draw.rect(screen, (255, 255, 255), btn_rect, width=3)
            
            text = font_large.render('TEST', True, (255, 255, 255))
            screen.blit(text, (btn_rect.centerx - text.get_width()//2, btn_rect.centery - text.get_height()//2))
            
            ind_color = (0, 255, 100) if btn_state else (80, 80, 80)
            pygame.draw.circle(screen, ind_color, (btn_rect.right - 40, btn_rect.centery), 10)
            
            coords = 'X:{:3d} Y:{:3d}'.format(x, y)
            screen.blit(font_small.render(coords, True, (255, 255, 0)), (10, HEIGHT - 80))
            
            status = 'PRESSED' if pressed else '------'
            screen.blit(font_small.render(status, True, (0, 255, 0) if pressed else (100, 100, 100)), (10, HEIGHT - 50))
            
            fb_update_fast(screen, fb_mem, line_length)
    
    except KeyboardInterrupt:
        pass
    finally:
        fb_mem.close()
        fb.close()
        pygame.quit()
    
    print('Stopped')

if __name__ == '__main__':
    main()

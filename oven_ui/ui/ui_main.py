#!/usr/bin/env python3
"""
Oven UI - Красивый интерфейс
Читает координаты из файла
"""

import os
import sys
import time
import struct
import fcntl
import mmap
import pygame
import math

# Конфигурация
WIDTH = 320
HEIGHT = 480
COORDS_FILE = '/tmp/touch_coords.dat'

# pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Цвета
COLOR_BG = (15, 15, 35)
COLOR_CARD = (30, 30, 60)
COLOR_ACCENT = (0, 180, 255)
COLOR_TEXT = (255, 255, 255)
COLOR_TEXT_DIM = (150, 150, 180)
COLOR_SUCCESS = (0, 255, 100)
COLOR_WARNING = (255, 180, 0)
COLOR_DANGER = (255, 50, 50)

class Button:
    def __init__(self, x, y, w, h, label, color_off, color_on):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.color_off = color_off
        self.color_on = color_on
        self.state = False
        self.anim = 0
        
    def update(self, dt):
        target = 1.0 if self.state else 0.0
        self.anim += (target - self.anim) * 10 * dt
        self.anim = max(0, min(1, self.anim))
        
    def draw(self, screen, font_large, font_small):
        r = int(self.color_off[0] + (self.color_on[0] - self.color_off[0]) * self.anim)
        g = int(self.color_off[1] + (self.color_on[1] - self.color_off[1]) * self.anim)
        b = int(self.color_off[2] + (self.color_on[2] - self.color_off[2]) * self.anim)
        color = (r, g, b)
        
        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        pygame.draw.rect(screen, COLOR_TEXT, self.rect, width=2, border_radius=15)
        
        # Индикатор
        ind_color = COLOR_SUCCESS if self.state else COLOR_TEXT_DIM
        ind_radius = 8 if self.state else 6
        pygame.draw.circle(screen, ind_color, (self.rect.right - 35, self.rect.centery), ind_radius)
        
        # Текст
        text = font_large.render(self.label, True, COLOR_TEXT)
        screen.blit(text, (self.rect.x + 20, self.rect.centery - text.get_height() // 2))
        
        status = "ON" if self.state else "OFF"
        status_text = font_small.render(status, True, COLOR_TEXT_DIM)
        screen.blit(status_text, (self.rect.right - 60, self.rect.centery - status_text.get_height() // 2))
    
    def check_touch(self, x, y):
        return self.rect.collidepoint(x, y)
    
    def toggle(self):
        self.state = not self.state


def read_touch():
    """Чтение из файла"""
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


def rgb565(r, g, b):
    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return bytes([color & 0xFF, (color >> 8) & 0xFF])


def fb_update(screen, fb_mem, line_length, WIDTH, HEIGHT):
    surface_data = pygame.surfarray.array3d(screen)
    fb_data = bytearray()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = surface_data[x][y]
            fb_data.extend(rgb565(r, g, b))
    fb_mem.seek(0)
    fb_mem.write(fb_data)


def draw_background(screen, time_val):
    for y in range(HEIGHT):
        r = int(15 + 10 * math.sin(time_val * 0.5 + y * 0.02))
        g = int(15 + 10 * math.sin(time_val * 0.3 + y * 0.015))
        b = int(35 + 20 * math.sin(time_val * 0.4 + y * 0.025))
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))


def main():
    print('=' * 40)
    print('OVEN UI - Starting')
    print('=' * 40)
    
    # Ждём файл с координатами
    print('Waiting for touch daemon...')
    for i in range(50):
        if os.path.exists(COORDS_FILE):
            print('Touch daemon found!')
            break
        time.sleep(0.1)
    else:
        print('ERROR: Touch daemon not running!')
        print('Run: sudo python3 daemon/touch_daemon.py &')
        return
    
    pygame.init()
    screen = pygame.Surface((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    font_large = pygame.font.Font(None, 42)
    font_small = pygame.font.Font(None, 28)
    font_title = pygame.font.Font(None, 56)
    
    fb = open('/dev/fb0', 'r+b')
    fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    if line_length == 0:
        line_length = WIDTH * 2
    fb_mem = mmap.mmap(fb.fileno(), line_length * HEIGHT, prot=mmap.PROT_WRITE)
    
    buttons = [
        Button(40, 80, 240, 65, 'LIGHT', (50, 50, 70), (255, 180, 0)),
        Button(40, 160, 240, 65, 'FAN', (50, 50, 70), (0, 180, 255)),
        Button(40, 240, 240, 65, 'HEATER', (50, 50, 70), (255, 50, 50)),
        Button(40, 320, 240, 65, 'PUMP', (50, 50, 70), (50, 255, 50)),
    ]
    
    title = font_title.render('OVEN CONTROL', True, COLOR_ACCENT)
    
    print('UI Ready! Touch the screen.')
    print('ESC to exit')
    print('=' * 40)
    
    running = True
    start_time = time.time()
    last_pressed = False
    
    try:
        while running:
            dt = clock.tick(60) / 1000.0
            time_val = time.time() - start_time
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
            
            # Чтение тачскрина
            x, y, pressed = read_touch()
            
            # Обработка нажатия (только один раз при нажатии)
            if pressed and not last_pressed:
                print('Touch: {},{}'.format(x, y))
                for btn in buttons:
                    if btn.check_touch(x, y):
                        btn.toggle()
                        print('  {} -> {}'.format(btn.label, 'ON' if btn.state else 'OFF'))
                        break
            
            last_pressed = pressed
            
            # Анимации
            for btn in buttons:
                btn.update(dt)
            
            # Отрисовка
            draw_background(screen, time_val)
            
            title_x = (WIDTH - title.get_width()) // 2
            screen.blit(title, (title_x, 20))
            
            subtitle = font_small.render('Touch to control', True, COLOR_TEXT_DIM)
            subtitle_x = (WIDTH - subtitle.get_width()) // 2
            screen.blit(subtitle, (subtitle_x, 60))
            
            for btn in buttons:
                btn.draw(screen, font_large, font_small)
            
            footer = font_small.render('ESC to exit', True, COLOR_TEXT_DIM)
            screen.blit(footer, (10, HEIGHT - 30))
            
            fb_update(screen, fb_mem, line_length, WIDTH, HEIGHT)
    
    except KeyboardInterrupt:
        pass
    finally:
        fb_mem.close()
        fb.close()
        pygame.quit()
        print('\nUI Stopped')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Simple Pygame app with one button - uses system touchscreen as mouse
Direct framebuffer output
"""

import os
import struct
import fcntl
import mmap
import pygame

# Конфигурация
WIDTH = 320
HEIGHT = 480

# pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Цвета
COLOR_BG = (20, 20, 40)
COLOR_BTN_OFF = (50, 50, 80)
COLOR_BTN_ON = (0, 200, 100)
COLOR_TEXT = (255, 255, 255)
COLOR_BORDER = (255, 255, 255)


def rgb565(r, g, b):
    """Конвертация RGB888 в RGB565"""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


class Button:
    def __init__(self, x, y, w, h, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.state = False
        
    def draw(self, screen, font):
        color = COLOR_BTN_ON if self.state else COLOR_BTN_OFF
        pygame.draw.rect(screen, color, self.rect, border_radius=20)
        pygame.draw.rect(screen, COLOR_BORDER, self.rect, width=3, border_radius=20)
        
        text = font.render(self.label, True, COLOR_TEXT)
        text_x = self.rect.centerx - text.get_width() // 2
        text_y = self.rect.centery - text.get_height() // 2
        screen.blit(text, (text_x, text_y))
        
        # Индикатор
        ind_color = (0, 255, 100) if self.state else (80, 80, 80)
        pygame.draw.circle(screen, ind_color, (self.rect.right - 40, self.rect.centery), 10)
        
    def toggle(self):
        self.state = not self.state
        return self.state


def main():
    print('=' * 40)
    print('SIMPLE TOUCHSCREEN TEST')
    print('=' * 40)
    
    pygame.init()
    screen = pygame.Surface((WIDTH, HEIGHT))
    font = pygame.font.Font(None, 48)
    font_title = pygame.font.Font(None, 36)
    
    # Открываем framebuffer
    try:
        fb = open('/dev/fb0', 'r+b')
        fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
        line_length = struct.unpack('I', fix_info[16:20])[0]
        if line_length == 0:
            line_length = WIDTH * 2
        print(f'Framebuffer: line_length={line_length}')
        fb_mem = mmap.mmap(fb.fileno(), line_length * HEIGHT, prot=mmap.PROT_WRITE)
        print('Framebuffer opened')
    except Exception as e:
        print(f'Framebuffer error: {e}')
        fb = None
        fb_mem = None
        line_length = WIDTH * 2
    
    # Кнопка
    button = Button(40, 200, 240, 80, 'TOUCH ME')
    
    print('Ready! Touch the button.')
    print('Press Ctrl+C to exit')
    print('=' * 40)
    
    running = True
    clock = pygame.time.Clock()
    
    try:
        while running:
            clock.tick(60)
            
            # Обработка событий pygame (тачскрин = мышь)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Нажатие на тачскрин
                    x, y = event.pos
                    print(f'Touch at: {x}, {y}')
                    if button.rect.collidepoint(x, y):
                        state = button.toggle()
                        print(f'  Button -> {"ON" if state else "OFF"}')
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Отрисовка
            screen.fill(COLOR_BG)
            
            # Заголовок
            title = font_title.render('Touchscreen Test', True, (100, 180, 255))
            title_x = (WIDTH - title.get_width()) // 2
            screen.blit(title, (title_x, 30))
            
            # Кнопка
            button.draw(screen, font)
            
            # Подсказка
            hint = font_title.render('Touch button', True, (80, 80, 100))
            screen.blit(hint, (10, HEIGHT - 40))
            
            # Вывод на framebuffer
            surface_data = pygame.surfarray.array3d(screen)
            fb_data = bytearray()
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    r, g, b = surface_data[x][y]
                    color = rgb565(r, g, b)
                    fb_data.append(color & 0xFF)
                    fb_data.append((color >> 8) & 0xFF)
            
            if fb_mem:
                fb_mem.seek(0)
                fb_mem.write(fb_data)
            
    except KeyboardInterrupt:
        print('\nInterrupted')
    finally:
        if fb_mem:
            fb_mem.close()
        if fb:
            fb.close()
        pygame.quit()
        print('Stopped')


if __name__ == '__main__':
    main()

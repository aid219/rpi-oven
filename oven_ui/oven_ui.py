#!/usr/bin/env python3
"""
Oven UI - ОДИН скрипт: тачскрин + интерфейс
Без разделения на демон и UI
"""

import os
import time
import struct
import fcntl
import mmap
import threading
import smbus
import RPi.GPIO as GPIO
import pygame

# Конфигурация
WIDTH = 320
HEIGHT = 480
TOUCH_ADDR = 0x38
RST_PIN = 27

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Общие данные тачскрина
touch_data = {'x': 0, 'y': 0, 'pressed': False, 'lock': threading.Lock()}

def touch_thread_func(bus):
    """Поток чтения тачскрина"""
    global touch_data
    was_touching = False
    
    while True:
        try:
            tc = bus.read_byte_data(TOUCH_ADDR, 0x02)
            if tc > 0:
                xh = bus.read_byte_data(TOUCH_ADDR, 0x03)
                xl = bus.read_byte_data(TOUCH_ADDR, 0x04)
                yh = bus.read_byte_data(TOUCH_ADDR, 0x05)
                yl = bus.read_byte_data(TOUCH_ADDR, 0x06)
                x = ((xh & 0x0F) << 8) | xl
                y = ((yh & 0x0F) << 8) | yl
                
                with touch_data['lock']:
                    touch_data['x'] = x
                    touch_data['y'] = y
                    touch_data['pressed'] = True
                was_touching = True
            else:
                if was_touching:
                    with touch_data['lock']:
                        touch_data['pressed'] = False
                was_touching = False
        except:
            pass
        time.sleep(0.02)

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

def main():
    print('=' * 40)
    print('OVEN UI - Starting')
    print('=' * 40)
    
    # Reset тачскрина
    print('Reset touch...')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RST_PIN, GPIO.OUT)
    GPIO.output(RST_PIN, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.2)
    # НЕ cleanup() - держим RESET в HIGH!
    
    # I2C
    bus = smbus.SMBus(1)
    print('I2C ready')
    
    # pygame
    pygame.init()
    screen = pygame.Surface((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)
    print('pygame ready')
    
    # Framebuffer
    fb = open('/dev/fb0', 'r+b')
    fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    if line_length == 0:
        line_length = WIDTH * 2
    fb_mem = mmap.mmap(fb.fileno(), line_length * HEIGHT, prot=mmap.PROT_WRITE)
    print('Framebuffer ready')
    
    # Запуск потока тачскрина
    touch_thread = threading.Thread(target=touch_thread_func, args=(bus,), daemon=True)
    touch_thread.start()
    print('Touch thread started')
    print('=' * 40)
    print('Ready! Touch the button')
    print('ESC to exit')
    print('=' * 40)
    
    # Кнопка
    btn_rect = pygame.Rect(40, 200, 240, 80)
    btn_state = False
    btn_anim = 0
    
    running = True
    last_pressed = False
    
    try:
        while running:
            dt = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
            
            # Чтение тачскрина из потока
            with touch_data['lock']:
                x = touch_data['x']
                y = touch_data['y']
                pressed = touch_data['pressed']
            
            # Обработка нажатия
            if pressed and not last_pressed:
                if btn_rect.collidepoint(x, y):
                    btn_state = not btn_state
                    print('Button -> {}'.format('ON' if btn_state else 'OFF'))
            
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
        bus.close()
        GPIO.cleanup()
        pygame.quit()
        print('\nStopped')

if __name__ == '__main__':
    main()

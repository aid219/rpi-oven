#!/usr/bin/env python3
"""
Кнопки на pygame с тачскрином + ОТЛАДКА
"""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import smbus
import time
import struct
import fcntl
import mmap
import RPi.GPIO as GPIO

WIDTH = 320
HEIGHT = 480
TOUCH_ADDR = 0x38
RST_PIN = 27

print("Reset...")
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.output(RST_PIN, GPIO.LOW)
time.sleep(0.1)
GPIO.output(RST_PIN, GPIO.HIGH)
time.sleep(0.1)
print("Reset OK")

try:
    bus = smbus.SMBus(1)
    print("I2C OK")
except:
    print("I2C FAIL - sudo modprobe i2c-dev")
    exit(1)

fb = open('/dev/fb0', 'r+b')
fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
line_length = struct.unpack('I', fix_info[16:20])[0]
if line_length == 0:
    line_length = WIDTH * 2
fb_mem = mmap.mmap(fb.fileno(), line_length * HEIGHT, prot=mmap.PROT_WRITE)

pygame.init()
screen = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def rgb565(r, g, b):
    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return bytes([color & 0xFF, (color >> 8) & 0xFF])

def get_touch_debug():
    """Чтение с отладкой"""
    try:
        touch_count = bus.read_byte_data(TOUCH_ADDR, 0x02)
        if touch_count > 0:
            xh = bus.read_byte_data(TOUCH_ADDR, 0x03)
            xl = bus.read_byte_data(TOUCH_ADDR, 0x04)
            yh = bus.read_byte_data(TOUCH_ADDR, 0x05)
            yl = bus.read_byte_data(TOUCH_ADDR, 0x06)
            x = ((xh & 0x0F) << 8) | xl
            y = ((yh & 0x0F) << 8) | yl
            return (x, y, touch_count)
        return None
    except Exception as e:
        print("I2C Error:", e)
        return None

buttons = [
    {'x': 40, 'y': 50, 'w': 240, 'h': 60, 'color_off': (50, 50, 50), 'color_on': (255, 180, 0), 'state': False, 'label': 'LIGHT'},
    {'x': 40, 'y': 130, 'w': 240, 'h': 60, 'color_off': (50, 50, 50), 'color_on': (0, 180, 255), 'state': False, 'label': 'FAN'},
    {'x': 40, 'y': 210, 'w': 240, 'h': 60, 'color_off': (50, 50, 50), 'color_on': (255, 50, 50), 'state': False, 'label': 'HEATER'},
    {'x': 40, 'y': 290, 'w': 240, 'h': 60, 'color_off': (50, 50, 50), 'color_on': (50, 255, 50), 'state': False, 'label': 'PUMP'},
]

def draw_button(btn):
    color = btn['color_on'] if btn['state'] else btn['color_off']
    rect = pygame.Rect(btn['x'], btn['y'], btn['w'], btn['h'])
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)
    ind_color = (0, 255, 0) if btn['state'] else (80, 80, 80)
    pygame.draw.rect(screen, ind_color, (btn['x'] + btn['w'] - 25, btn['y'] + 8, 15, 15))
    font = pygame.font.Font(None, 36)
    text = font.render(btn['label'], True, (255, 255, 255))
    text_x = btn['x'] + (btn['w'] - text.get_width()) // 2
    screen.blit(text, (text_x, btn['y'] + btn['h'] // 2 - 3))

def fb_update():
    surface_data = pygame.surfarray.array3d(screen)
    fb_data = bytearray()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = surface_data[x][y]
            fb_data.extend(rgb565(r, g, b))
    fb_mem.seek(0)
    fb_mem.write(fb_data)

# ТЕСТ ТАЧСКРИНА ПЕРЕД ЗАПУСКОМ
print("\nТЕСТ ТАЧСКРИНА (5 сек)...")
for i in range(100):
    touch = get_touch_debug()
    if touch:
        print("  TOUCH DETECTED! x={}, y={}, tc={}".format(touch[0], touch[1], touch[2]))
    time.sleep(0.05)

print("\nЗапуск интерфейса...")
print("Коснитесь экрана для теста\n")

last_touch_time = 0
was_touching = False
touch_count_total = 0
btn_touches = 0

running = True
try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Читаем тачскрин КАЖДЫЙ цикл
        touch = get_touch_debug()
        
        if touch:
            touch_count_total += 1
            x, y, tc = touch
            
            if not was_touching:
                current_time = time.time()
                if current_time - last_touch_time > 0.3:
                    print("Touch #{}, x={}, y={}, tc={}".format(touch_count_total, x, y, tc))
                    
                    # Проверка кнопок
                    for btn in buttons:
                        if (btn['x'] <= x <= btn['x'] + btn['w'] and
                            btn['y'] <= y <= btn['y'] + btn['h']):
                            btn['state'] = not btn['state']
                            btn_touches += 1
                            print("  >>> {} #{} -> {}".format(btn['label'], btn_touches, "ON" if btn['state'] else "OFF"))
                            last_touch_time = current_time
                            break
                    
                    was_touching = True
        else:
            was_touching = False
        
        # Отрисовка
        screen.fill((20, 20, 30))
        for btn in buttons:
            draw_button(btn)
        
        # Статистика
        font = pygame.font.Font(None, 28)
        stats = "Touches:{} Btn:{}".format(touch_count_total, btn_touches)
        stats_surf = font.render(stats, True, (255, 255, 0))
        screen.blit(stats_surf, (10, 410))
        
        fb_update()
        clock.tick(30)

except KeyboardInterrupt:
    pass
finally:
    fb_mem.close()
    fb.close()
    bus.close()
    GPIO.cleanup()
    pygame.quit()
    print("\nDone! Total touches={}, btn={}".format(touch_count_total, btn_touches))

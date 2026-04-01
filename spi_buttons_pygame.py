#!/usr/bin/env python3
"""
Кнопки pygame + тачскрин - АСИНХРОННО (threading)
Сенсор в отдельном потоке, отрисовка в главном
"""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import smbus
import time
import struct
import fcntl
import mmap
import RPi.GPIO as GPIO
import threading
import pygame

WIDTH = 320
HEIGHT = 480
TOUCH_ADDR = 0x38
RST_PIN = 27

# Общие данные
touch_data = {'x': 0, 'y': 0, 'pressed': False, 'lock': threading.Lock()}
buttons_lock = threading.Lock()

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
print("FB OK")

# pygame
pygame.init()
screen = pygame.Surface((WIDTH, HEIGHT))
print("pygame OK")

clock = pygame.time.Clock()

def rgb565(r, g, b):
    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return bytes([color & 0xFF, (color >> 8) & 0xFF])

def touch_thread_func():
    """Поток чтения тачскрина"""
    global touch_data
    was_touching = False
    
    while True:
        try:
            touch_count = bus.read_byte_data(TOUCH_ADDR, 0x02)
            if touch_count > 0:
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
        time.sleep(0.02)  # 50Hz опрос

# Запуск потока сенсора
touch_thread = threading.Thread(target=touch_thread_func, daemon=True)
touch_thread.start()
print("Touch thread started")

buttons = [
    {'x': 40, 'y': 50, 'w': 240, 'h': 60, 'color_off': (50, 50, 50), 'color_on': (255, 180, 0), 'state': False, 'label': 'LIGHT'},
    {'x': 40, 'y': 130, 'w': 240, 'h': 60, 'color_off': (50, 50, 50), 'color_on': (0, 180, 255), 'state': False, 'label': 'FAN'},
    {'x': 40, 'y': 210, 'w': 240, 'h': 60, 'color_off': (50, 50, 50), 'color_on': (255, 50, 50), 'state': False, 'label': 'HEATER'},
    {'x': 40, 'y': 290, 'w': 240, 'h': 60, 'color_off': (50, 50, 50), 'color_on': (50, 255, 50), 'state': False, 'label': 'PUMP'},
]

def draw_button(btn):
    color = btn['color_on'] if btn['state'] else btn['color_off']
    pygame.draw.rect(screen, color, (btn['x'], btn['y'], btn['w'], btn['h']))
    pygame.draw.rect(screen, (255, 255, 255), (btn['x'], btn['y'], btn['w'], btn['h']), 2)
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

# Отрисовка ПЕРЕД циклом
screen.fill((20, 20, 30))
for btn in buttons:
    draw_button(btn)
fb_update()

print("\nГотово! Коснитесь экрана.")
print("ESC для выхода\n")

last_touch_time = 0
was_pressed = False
touch_total = 0
btn_total = 0

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                raise KeyboardInterrupt()
        
        # Читаем touch_data из потока
        with touch_data['lock']:
            x = touch_data['x']
            y = touch_data['y']
            pressed = touch_data['pressed']
        
        # Обработка нажатия
        if pressed and not was_pressed:
            current_time = time.time()
            if current_time - last_touch_time > 0.5:  # Антидребезг
                touch_total += 1
                print("Touch #{} x={}, y={}".format(touch_total, x, y))
                
                with buttons_lock:
                    for btn in buttons:
                        if (btn['x'] <= x <= btn['x'] + btn['w'] and
                            btn['y'] <= y <= btn['y'] + btn['h']):
                            btn['state'] = not btn['state']
                            btn_total += 1
                            print("  {} -> {}".format(btn['label'], "ON" if btn['state'] else "OFF"))
                            last_touch_time = current_time
                            break
        
        was_pressed = pressed
        
        # Отрисовка
        screen.fill((20, 20, 30))
        with buttons_lock:
            for btn in buttons:
                draw_button(btn)
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
    print("\nDone! Touches={} Btn={}".format(touch_total, btn_total))

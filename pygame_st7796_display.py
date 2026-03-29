#!/usr/bin/env python3
"""
Pygame на SPI дисплей ST7796U - без использования SDL display
"""

import spidev
import RPi.GPIO as GPIO
import time
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame

# GPIO пины
DC_PIN = 25
RST_PIN = 24
BL_PIN = 18

# Разрешение дисплея
WIDTH = 320
HEIGHT = 480

# Инициализация GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DC_PIN, GPIO.OUT)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.setup(BL_PIN, GPIO.OUT)
GPIO.output(BL_PIN, GPIO.HIGH)

# SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 62000000
spi.mode = 0

def write_command(cmd):
    GPIO.output(DC_PIN, GPIO.LOW)
    spi.xfer2([cmd])

def write_data(data):
    GPIO.output(DC_PIN, GPIO.HIGH)
    if isinstance(data, list) and len(data) > 0:
        spi.xfer2(data)

def write_command_data(cmd, data=None):
    write_command(cmd)
    if data is not None:
        write_data(data)

def init_display():
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.01)
    GPIO.output(RST_PIN, GPIO.LOW)
    time.sleep(0.01)
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.12)
    
    write_command(0x01)
    time.sleep(0.12)
    write_command(0x11)
    time.sleep(0.15)
    write_command_data(0xF0, [0xC3])
    write_command_data(0xF0, [0x96])
    write_command_data(0x36, [0x48])
    write_command_data(0x3A, [0x55])
    write_command_data(0xB4, [0x01])
    write_command_data(0xB6, [0x80, 0x02, 0x3B])
    write_command_data(0xE8, [0x40, 0x8A, 0x00, 0x00, 0x29, 0x19, 0xA5, 0x33])
    write_command_data(0xC1, [0x06])
    write_command_data(0xC2, [0xA7])
    write_command_data(0xC5, [0x18])
    write_command_data(0xE0, [0xF0, 0x09, 0x0B, 0x06, 0x04, 0x15, 0x2F, 0x54, 0x42, 0x3C, 0x17, 0x14, 0x18, 0x1B])
    write_command_data(0xE1, [0xE0, 0x09, 0x0B, 0x06, 0x04, 0x03, 0x2B, 0x43, 0x42, 0x3B, 0x16, 0x14, 0x17, 0x1B])
    write_command_data(0xF0, [0x3C])
    write_command_data(0xF0, [0x69])
    write_command(0x29)
    write_command_data(0x2A, [0x00, 0x00, 0x01, 0x3F])
    write_command_data(0x2B, [0x00, 0x00, 0x01, 0xDF])

def set_window(x1, y1, x2, y2):
    write_command_data(0x2A, [(x1 >> 8) & 0xFF, x1 & 0xFF, (x2 >> 8) & 0xFF, x2 & 0xFF])
    write_command_data(0x2B, [(y1 >> 8) & 0xFF, y1 & 0xFF, (y2 >> 8) & 0xFF, y2 & 0xFF])
    write_command(0x2C)

def draw_surface_fast(surface):
    """Быстрая отправка Pygame surface на дисплей"""
    set_window(0, 0, WIDTH-1, HEIGHT-1)
    GPIO.output(DC_PIN, GPIO.HIGH)
    
    # Конвертируем в RGB565 быстро
    pixels_32bit = pygame.image.tostring(surface, 'RGB')
    
    data = []
    for i in range(0, len(pixels_32bit), 3):
        r = ord(pixels_32bit[i]) if isinstance(pixels_32bit[i], str) else pixels_32bit[i]
        g = ord(pixels_32bit[i+1]) if isinstance(pixels_32bit[i+1], str) else pixels_32bit[i+1]
        b = ord(pixels_32bit[i+2]) if isinstance(pixels_32bit[i+2], str) else pixels_32bit[i+2]
        color = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
        data.extend([(color >> 8) & 0xFF, color & 0xFF])
    
    chunk_size = 4096
    for i in range(0, len(data), chunk_size):
        spi.xfer2(data[i:i+chunk_size])

print("Инициализация дисплея...")
init_display()

print("Инициализация Pygame (dummy driver)...")
pygame.init()
pygame.display.set_mode((WIDTH, HEIGHT), 0)

# Создаём surface для дисплея
display_surface = pygame.Surface((WIDTH, HEIGHT))

print("Запуск цикла (30 секунд)...")
clock = pygame.time.Clock()
start_time = time.time()
angle = 0

try:
    while time.time() - start_time < 30:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    raise KeyboardInterrupt()
        
        # Очистка
        display_surface.fill((0, 0, 0))
        
        # Рисуем фигуры
        pygame.draw.rect(display_surface, (255, 0, 0), pygame.Rect(20, 20, 100, 100))
        pygame.draw.circle(display_surface, (0, 255, 0), (230, 70), 50)
        pygame.draw.ellipse(display_surface, (0, 0, 255), pygame.Rect(100, 150, 120, 80))
        
        # Текст
        font = pygame.font.Font(None, 36)
        text = font.render("Hello!", True, (255, 255, 255))
        display_surface.blit(text, (100, 250))
        
        text2 = font.render("Pygame", True, (255, 255, 0))
        display_surface.blit(text2, (90, 290))
        
        # Анимация
        angle += 2
        end_x = 160 + int(50 * pygame.math.Vector2(1, 0).rotate(angle).x)
        end_y = 350 + int(50 * pygame.math.Vector2(1, 0).rotate(angle).y)
        pygame.draw.line(display_surface, (255, 255, 255), (160, 350), (end_x, end_y), 3)
        
        # Отправляем на дисплей
        draw_surface_fast(display_surface)
        
        clock.tick(30)
        print(f"FPS: {int(clock.get_fps())}", end='\r')
        
except KeyboardInterrupt:
    print("\nВыход...")

finally:
    display_surface.fill((0, 0, 0))
    draw_surface_fast(display_surface)
    GPIO.output(BL_PIN, GPIO.LOW)
    GPIO.cleanup()
    spi.close()
    pygame.quit()

print("\nГотово!")

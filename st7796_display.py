#!/usr/bin/env python3
"""
ST7796U - тест с командой подсветки
"""

import spidev
import RPi.GPIO as GPIO
import time
from PIL import Image, ImageDraw

DC_PIN = 25
RST_PIN = 24
BL_PIN = 18

WIDTH = 320
HEIGHT = 480

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DC_PIN, GPIO.OUT)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.setup(BL_PIN, GPIO.OUT)

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

def clear_screen():
    write_command(0x2C)
    GPIO.output(DC_PIN, GPIO.HIGH)
    for _ in range(WIDTH * HEIGHT):
        spi.xfer2([0, 0])

def set_window(x1, y1, x2, y2):
    write_command_data(0x2A, [(x1 >> 8) & 0xFF, x1 & 0xFF, (x2 >> 8) & 0xFF, x2 & 0xFF])
    write_command_data(0x2B, [(y1 >> 8) & 0xFF, y1 & 0xFF, (y2 >> 8) & 0xFF, y2 & 0xFF])
    write_command(0x2C)

def draw_image(image):
    set_window(0, 0, WIDTH-1, HEIGHT-1)
    GPIO.output(DC_PIN, GPIO.HIGH)
    rgb_image = image.convert('RGB')
    pixels = rgb_image.tobytes()
    data = []
    for i in range(0, len(pixels), 3):
        r, g, b = pixels[i], pixels[i+1] if i+1<len(pixels) else 0, pixels[i+2] if i+2<len(pixels) else 0
        color = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
        data.extend([(color >> 8) & 0xFF, color & 0xFF])
    for i in range(0, len(data), 4096):
        spi.xfer2(data[i:i+4096])

print("Инициализация...")
init_display()

# Тест BL пина
print("BL = HIGH...")
GPIO.output(BL_PIN, GPIO.HIGH)
time.sleep(1)

clear_screen()

print("Белый экран...")
img = Image.new('RGB', (WIDTH, HEIGHT), color='white')
draw_image(img)
time.sleep(3)

print("BL = LOW...")
GPIO.output(BL_PIN, GPIO.LOW)
time.sleep(2)

print("BL = HIGH...")
GPIO.output(BL_PIN, GPIO.HIGH)
time.sleep(2)

print("Текст...")
img = Image.new('RGB', (WIDTH, HEIGHT), color='black')
draw = ImageDraw.Draw(img)
draw.text((50, 200), "Hello!", fill=(255, 255, 255))
draw.text((30, 240), "Raspberry Pi", fill=(255, 255, 0))
draw.text((60, 280), "ST7796U", fill=(0, 255, 255))
draw_image(img)

print("Держим 60 сек...")
time.sleep(60)

print("Готово!")
spi.close()

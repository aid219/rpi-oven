#!/usr/bin/env python3
"""
Тестовый скрипт для IPS дисплея ST7796U через st7789 драйвер
"""

from luma.lcd.device import st7789
from luma.core.interface.serial import spi
from luma.core.render import canvas
import time

# SPI интерфейс с GPIO пинами
spi_interface = spi(
    port=0,
    device=0,
    gpio_DC=25,
    gpio_RST=24,
    bus_speed_hz=40000000
)

# Инициализация дисплея
device = st7789(
    serial_interface=spi_interface,
    rotate=0,
    width=320,
    height=480
)

print("Дисплей инициализирован...")
time.sleep(1)

# Тесты
print("Тест 1: Белый экран...")
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="white")
time.sleep(2)

print("Тест 2: Чёрный экран...")
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="black", fill="black")
time.sleep(1)

print("Тест 3: Цветные полосы...")
with canvas(device) as draw:
    draw.rectangle([0, 0, 319, 159], outline="red", fill="red")
    draw.rectangle([0, 160, 319, 319], outline="green", fill="green")
    draw.rectangle([0, 320, 319, 479], outline="blue", fill="blue")
time.sleep(2)

print("Тест 4: Текст и фигуры...")
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="black", fill="black")
    draw.ellipse([20, 20, 120, 120], outline="red", fill="red")
    draw.ellipse([180, 20, 280, 120], outline="green", fill="green")
    draw.ellipse([100, 140, 200, 240], outline="blue", fill="blue")
    draw.text((50, 200), "Hello!", fill="white")
    draw.text((30, 240), "Raspberry Pi", fill="yellow")
    draw.text((60, 280), "ST7796U", fill="cyan")
time.sleep(3)

print("Тест 5: Радуга...")
colors = ["red", "green", "blue", "yellow", "cyan", "magenta", "white"]
for color in colors:
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline=color, fill=color)
    time.sleep(0.5)

print("Готово!")
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="black", fill="black")
    draw.text((60, 230), "Done!", fill="white")
time.sleep(3)

#!/usr/bin/env python3
"""Главный файл для энкодера"""
import os
import sys
import signal
import time
import pygame

# PID файл
PID_FILE = '/tmp/encoder.pid'

# Импорт компонентов
from encoder_handler import Encoder
from interface_encoder import UI

# Глобальные
encoder = None
running = True

def cleanup():
    global running
    running = False
    if encoder:
        encoder.stop()
    try:
        os.remove(PID_FILE)
    except:
        pass

def handler(sig, frame):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

# Инициализация
ui = UI('config_encoder.json')
encoder = Encoder(clk_pin=5, dt_pin=6)

# Callback на изменение значения
def on_value_change(value):
    ui.set_value(value)

encoder.add_callback(on_value_change)

# PID
with open(PID_FILE, 'w') as f:
    f.write(str(os.getpid()))

# Главный цикл
clock = pygame.time.Clock()

while running:
    # События UI
    action = ui.handle_input()
    if action == 'quit':
        break
    if action == 'reset':
        encoder.set_value(0)
    
    # Отрисовка
    ui.draw()
    
    # 30 FPS
    clock.tick(30)

cleanup()
print("Encoder stopped")

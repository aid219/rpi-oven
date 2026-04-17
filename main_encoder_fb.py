#!/usr/bin/env python3
"""Главный файл для энкодера — оптимизированная версия"""
import os
import sys
import signal
import time
import pygame

# PID файл
PID_FILE = '/tmp/encoder.pid'

# Логирование времени
start_time = time.time()
print(f"[{time.time()-start_time:.2f}s] Старт...")

# Импорт компонентов
from encoder_handler1 import Encoder
from interface_encoder_fb import UI

print(f"[{time.time()-start_time:.2f}s] Импорт готов")

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

print(f"[{time.time()-start_time:.2f}s] Signal handlers OK")

# Инициализация
ui = UI('config_encoder.json')
print(f"[{time.time()-start_time:.2f}s] UI создан")

encoder = Encoder(clk_pin=5, dt_pin=6)
print(f"[{time.time()-start_time:.2f}s] Энкодер создан")

# Callback на изменение значения
def on_value_change(value):
    ui.set_value(value)

encoder.add_callback(on_value_change)
print(f"[{time.time()-start_time:.2f}s] Callback добавлен")

# PID
with open(PID_FILE, 'w') as f:
    f.write(str(os.getpid()))

print(f"[{time.time()-start_time:.2f}s] Готово! Запуск цикла...")

# Главный цикл
clock = pygame.time.Clock()

while running:
    # События UI
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                break
            if event.key == pygame.K_SPACE:
                encoder.set_value(0)
    
    # Отрисовка
    ui.draw()
    
    # 30 FPS
    clock.tick(30)

cleanup()
print("Encoder stopped")

#!/usr/bin/env python3
"""Тестовый скрипт для UART сканера QR-кодов"""
import os
import sys
import signal
import time
import pygame
import serial

# PID файл
PID_FILE = '/tmp/scanner.pid'

# UART настройки
UART_PORT = '/dev/serial0'  # или /dev/ttyAMA0
BAUD_RATE = 9600
TIMEOUT = 1

# Глобальные
running = True
last_scan = ""
scan_time = 0

def cleanup():
    global running
    running = False
    try:
        os.remove(PID_FILE)
    except:
        pass

def handler(sig, frame):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

# Инициализация UART
try:
    ser = serial.Serial(UART_PORT, BAUD_RATE, timeout=TIMEOUT)
    print(f"UART подключен: {UART_PORT}")
except Exception as e:
    print(f"Ошибка UART: {e}")
    print("Проверьте:")
    print("  1. Включен ли UART в /boot/config.txt (enable_uart=1)")
    print("  2. Правильный ли порт (/dev/serial0, /dev/ttyAMA0, /dev/ttyS0)")
    print("  3. Подключение проводов (TX→RX, RX→TX)")
    ser = None

# PID
with open(PID_FILE, 'w') as f:
    f.write(str(os.getpid()))

# Инициализация Pygame
pygame.init()
pygame.font.init()

width = 1024
height = 600

os.system('setterm -blank 0 2>/dev/null')
os.system('setterm -cursor off 2>/dev/null')

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('QR Scanner')
clock = pygame.time.Clock()
big_font = pygame.font.Font(None, 72)
font = pygame.font.Font(None, 36)

def draw():
    global last_scan, scan_time
    
    # Фон
    screen.fill((30, 30, 50))
    
    # Заголовок
    title = big_font.render("QR Scanner", True, (255, 255, 255))
    title_rect = title.get_rect(center=(width // 2, 100))
    screen.blit(title, title_rect)
    
    # Статус UART
    if ser:
        status = font.render(f"UART: {UART_PORT} [{BAUD_RATE}]", True, (100, 255, 100))
    else:
        status = font.render("UART: НЕ ПОДКЛЮЧЕН", True, (255, 100, 100))
    screen.blit(status, (50, 180))
    
    # Последний скан
    scan_label = font.render("Последний скан:", True, (200, 200, 200))
    screen.blit(scan_label, (50, 250))
    
    if last_scan:
        # Разбиваем длинную строку на части
        max_width = width - 100
        words = last_scan.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + ' '
            test_surf = font.render(test_line, True, (255, 255, 255))
            if test_surf.get_width() > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = word + ' '
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)
        
        for i, line in enumerate(lines[:5]):  # Максимум 5 строк
            scan_text = font.render(line.strip(), True, (255, 255, 255))
            screen.blit(scan_text, (70, 290 + i * 40))
        
        # Время сканирования
        elapsed = time.time() - scan_time
        time_text = font.render(f"{elapsed:.1f} сек назад", True, (150, 150, 150))
        screen.blit(time_text, (70, 290 + len(lines[:5]) * 40 + 20))
    else:
        no_scan = font.render("Нет данных", True, (150, 150, 150))
        screen.blit(no_scan, (70, 290))
    
    # Подсказка
    hint = font.render("Нажмите ESC для выхода", True, (100, 100, 100))
    hint_rect = hint.get_rect(center=(width // 2, height - 50))
    screen.blit(hint, hint_rect)
    
    pygame.display.flip()

def read_uart():
    global last_scan, scan_time
    
    if not ser:
        return
    
    try:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            if data:
                last_scan = data
                scan_time = time.time()
                print(f"Скан: {data}")
    except Exception as e:
        print(f"Ошибка чтения UART: {e}")

# Главный цикл
print("Запуск... Нажмите ESC для выхода")

while running:
    # События
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Чтение UART
    read_uart()
    
    # Отрисовка
    draw()
    
    # 30 FPS
    clock.tick(30)

# Очистка
if ser:
    ser.close()

cleanup()
pygame.quit()
print("Остановлено")

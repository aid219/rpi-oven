#!/usr/bin/env python3
"""Тест сенсорного экрана"""
import struct
import os

print("=== Поиск сенсорного экрана ===\n")

# Проверяем все input устройства
for i in range(5):
    event_path = f'/dev/input/event{i}'
    try:
        # Читаем имя устройства
        name_path = f'/sys/class/input/event{i}/device/name'
        with open(name_path) as f:
            name = f.read().strip()
        
        print(f"event{i}: {name}")
        
        # Проверяем, есть ли ABS события (сенсор)
        abs_path = f'/sys/class/input/event{i}/device/capabilities/abs'
        try:
            with open(abs_path) as f:
                caps = f.read().strip()
                if caps:
                    print(f"  -> ABS events: {caps} (это сенсор!)")
        except:
            pass
    except Exception as e:
        print(f"event{i}: не доступно ({e})")

print("\n=== Тест нажатий ===")
print("Найди устройство с ABS и нажми Ctrl+C для выхода\n")

# Открываем первое устройство с ABS
touch_fd = None
for i in range(5):
    try:
        touch_fd = open(f'/dev/input/event{i}', 'rb')
        print(f"Открыт {event_path}")
        break
    except:
        continue

if not touch_fd:
    print("Не найдено input устройств!")
    exit(1)

try:
    while True:
        event = touch_fd.read(24)
        if len(event) >= 24:
            _, _, etype, code, value = struct.unpack('llHHi', event)
            
            # EV_ABS = 3
            if etype == 3:
                if code == 0:
                    print(f"X: {value}", end='\r')
                elif code == 1:
                    print(f"Y: {value}", end='\r')
                elif code == 24:  # давление
                    if value > 0:
                        print(f"\nTOUCH DOWN! pressure={value}")
                    else:
                        print(f"\nTOUCH UP!")
except KeyboardInterrupt:
    print("\nГотово!")
finally:
    touch_fd.close()

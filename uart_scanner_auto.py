#!/usr/bin/env python3
"""UART сканер с автоподбором скорости"""
import serial
import sys
import time

UART_PORT = '/dev/serial0'
BAUD_RATES = [9600, 115200, 57600, 38400, 19200]

print("Поиск правильной скорости UART...", flush=True)

for baud in BAUD_RATES:
    try:
        print(f"  Пробую {baud}...", flush=True)
        ser = serial.Serial(UART_PORT, baud, timeout=0.5)
        time.sleep(0.1)
        
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            if data:
                print(f"✓ Нашел данные на {baud}!", flush=True)
                print(f"  Данные: {data}", flush=True)
                ser.close()
                
                # Запускаем чтение на этой скорости
                print(f"\n=== Запуск на скорости {baud} ===", flush=True)
                ser = serial.Serial(UART_PORT, baud, timeout=None)
                line = bytearray()
                
                while True:
                    byte = ser.read(1)
                    if byte:
                        if byte == b'\n':
                            text = line.decode('utf-8', errors='ignore').strip()
                            if text:
                                print(f"→ {text}", flush=True)
                            line = bytearray()
                        elif byte != b'\r':
                            line.append(byte[0])
        else:
            ser.close()
            time.sleep(0.2)
            
    except Exception as e:
        print(f"  ✗ {baud}: {e}", flush=True)

print("\nНе удалось найти активный порт", flush=True)

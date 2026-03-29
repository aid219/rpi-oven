#!/usr/bin/env python3
"""UART сканер QR-кодов"""
import serial

ser = serial.Serial('/dev/serial0', 115200, timeout=None)
print("📡 Сканер запущен [115200]", flush=True)

line = bytearray()

while True:
    b = ser.read(1)
    if b == b'\n':
        text = line.decode('utf-8', errors='ignore').strip()
        if text:
            print(f"→ {text}", flush=True)
        line = bytearray()
    elif b == b'\r':
        pass
    elif b:
        line.append(b[0])

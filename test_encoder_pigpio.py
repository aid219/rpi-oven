#!/usr/bin/env python3
"""Тест энкодера на pigpio (прерывания)"""
from encoder import Encoder

def on_change(value):
    print(f"  -> value = {value}")

enc = Encoder(clk_pin=5, dt_pin=6, callback=on_change)
print("Крути энкодер... (Ctrl+C для выхода)")

try:
    import time
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    enc.stop()
    print("\nВыход")

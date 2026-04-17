#!/usr/bin/env python3
"""Тест энкодера polling методом"""
import RPi.GPIO as GPIO
import time

CLK_PIN = 5
DT_PIN = 6

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.cleanup([CLK_PIN, DT_PIN])
GPIO.setup(CLK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_clk = GPIO.input(CLK_PIN)
value = 0

print(f"Encoder polling test: CLK=BCM{CLK_PIN}, DT=BCM{DT_PIN}")
print("Крути энкодер... (Ctrl+C для выхода)")

try:
    while True:
        clk = GPIO.input(CLK_PIN)
        dt = GPIO.input(DT_PIN)
        
        if last_clk == 0 and clk == 1:
            if dt == 0:
                value += 1
            else:
                value -= 1
            print(f"  -> value = {value}")
        
        last_clk = clk
        time.sleep(0.001)  # 1ms poll
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nВыход")

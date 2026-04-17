#!/usr/bin/env python3
"""Тест энкодера без интерфейса"""
import RPi.GPIO as GPIO
import time
import sys

CLK_PIN = 5
DT_PIN = 6

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.cleanup([CLK_PIN, DT_PIN])
GPIO.setup(CLK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_clk = GPIO.input(CLK_PIN)
value = 0

print(f"Encoder test: CLK=BCM{CLK_PIN}, DT=BCM{DT_PIN}")
print("Крути энкодер... (Ctrl+C для выхода)")

def callback(channel):
    global value, last_clk
    clk = GPIO.input(CLK_PIN)
    dt = GPIO.input(DT_PIN)
    
    if last_clk == 0 and clk == 1:
        if dt == 0:
            value += 1
        else:
            value -= 1
        print(f"  -> value = {value}")
    
    last_clk = clk

GPIO.add_event_detect(CLK_PIN, GPIO.BOTH, callback=callback, bouncetime=5)

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nВыход")

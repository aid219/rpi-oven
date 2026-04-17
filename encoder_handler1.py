#!/usr/bin/env python3
"""Обработчик энкодера — только восходящий фронт CLK"""
import RPi.GPIO as GPIO
import threading

class Encoder:
    def __init__(self, clk_pin=5, dt_pin=6):
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.value = 0
        self.lock = threading.Lock()
        self.callbacks = []
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Полный cleanup перед инициализацией
        GPIO.cleanup([clk_pin, dt_pin])
        GPIO.setup(clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Запоминаем предыдущее состояние
        self.last_clk = GPIO.input(clk_pin)
        self.last_dt = GPIO.input(dt_pin)

        self.running = True

        # Прерывания только на CLK
        GPIO.add_event_detect(clk_pin, GPIO.BOTH, callback=self._callback, bouncetime=5)
    
    def _callback(self, channel):
        if not self.running:
            return
        
        clk = GPIO.input(self.clk_pin)
        dt = GPIO.input(self.dt_pin)
        
        # Детектируем только восходящий фронт CLK (0→1)
        if self.last_clk == 0 and clk == 1:
            # Смотрим состояние DT в этот момент
            if dt == 0:
                self._change_value(1)   # Вправо
            else:
                self._change_value(-1)  # Влево
        
        self.last_clk = clk
        self.last_dt = dt
    
    def _change_value(self, delta):
        with self.lock:
            self.value += delta
            for callback in self.callbacks:
                callback(self.value)
    
    def add_callback(self, callback):
        self.callbacks.append(callback)
    
    def get_value(self):
        with self.lock:
            return self.value
    
    def set_value(self, value):
        with self.lock:
            self.value = value
            for callback in self.callbacks:
                callback(self.value)
    
    def stop(self):
        self.running = False
        GPIO.remove_event_detect(self.clk_pin)
        GPIO.cleanup([self.clk_pin, self.dt_pin])

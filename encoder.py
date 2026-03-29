#!/usr/bin/env python3
"""
Библиотека для работы с инкрементальным энкодером на Raspberry Pi.
Использует аппаратные прерывания GPIO для мгновенной реакции.

Пример использования:
    from encoder import Encoder
    
    def on_change(value):
        print(f"Новое значение: {value}")
    
    encoder = Encoder(clk_pin=5, dt_pin=6, callback=on_change)
    
    # Получение текущего значения
    value = encoder.get_value()
    
    # Установка значения
    encoder.set_value(100)
    
    # Остановка
    encoder.stop()
"""

import RPi.GPIO as GPIO
import threading
from typing import Callable, Optional


class Encoder:
    """
    Класс для обработки сигналов инкрементального энкодера.
    
    Атрибуты:
        clk_pin (int): GPIO пин для сигнала CLK
        dt_pin (int): GPIO пин для сигнала DT
        value (int): Текущее значение энкодера
    """
    
    def __init__(
        self,
        clk_pin: int = 5,
        dt_pin: int = 6,
        callback: Optional[Callable[[int], None]] = None,
        initial_value: int = 0
    ):
        """
        Инициализация энкодера.
        
        Args:
            clk_pin: GPIO пин для CLK (по умолчанию 5)
            dt_pin: GPIO пин для DT (по умолчанию 6)
            callback: Функция обратного вызова при изменении значения
            initial_value: Начальное значение (по умолчанию 0)
        """
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self._value = initial_value
        self._lock = threading.Lock()
        self._callbacks = []
        self._running = True
        
        # Настройка GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Запоминаем начальное состояние
        self._last_clk = GPIO.input(clk_pin)
        self._last_dt = GPIO.input(dt_pin)
        
        # Добавляем callback если есть
        if callback:
            self.add_callback(callback)
        
        # Регистрируем прерывание только на CLK (оба фронта)
        GPIO.add_event_detect(clk_pin, GPIO.BOTH, callback=self._isr)
    
    def _isr(self, channel: int) -> None:
        """
        Прерывание (ISR) - вызывается при изменении CLK.
        Детектирует направление по восходящему фронту CLK и состоянию DT.
        """
        if not self._running:
            return
        
        clk = GPIO.input(self.clk_pin)
        dt = GPIO.input(self.dt_pin)
        
        # Детектируем только восходящий фронт CLK (0→1)
        if self._last_clk == 0 and clk == 1:
            # Смотрим состояние DT в этот момент
            if dt == 0:
                self._change_value(1)   # Вращение вправо
            else:
                self._change_value(-1)  # Вращение влево
        
        self._last_clk = clk
        self._last_dt = dt
    
    def _change_value(self, delta: int) -> None:
        """Изменение значения и вызов callback."""
        with self._lock:
            self._value += delta
            current_value = self._value
        
        # Вызываем все callback
        for callback in self._callbacks:
            callback(current_value)
    
    def add_callback(self, callback: Callable[[int], None]) -> None:
        """
        Добавить функцию обратного вызова.
        
        Args:
            callback: Функция, принимающая текущее значение (int)
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[int], None]) -> None:
        """Удалить функцию обратного вызова."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def get_value(self) -> int:
        """Получить текущее значение энкодера."""
        with self._lock:
            return self._value
    
    def set_value(self, value: int) -> None:
        """
        Установить новое значение энкодера.
        
        Args:
            value: Новое значение
        """
        with self._lock:
            self._value = value
        
        # Вызываем callback с новым значением
        for callback in self._callbacks:
            callback(value)
    
    def reset(self) -> None:
        """Сбросить значение в 0."""
        self.set_value(0)
    
    def stop(self) -> None:
        """Остановить обработку и освободить GPIO."""
        self._running = False
        GPIO.remove_event_detect(self.clk_pin)
        GPIO.cleanup([self.clk_pin, self.dt_pin])
    
    def __enter__(self):
        """Контекстный менеджер: вход."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер: выход."""
        self.stop()
        return False


# Для совместимости
IncrementalEncoder = Encoder

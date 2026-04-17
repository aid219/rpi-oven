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

import pigpio
import threading
from typing import Callable, Optional


class Encoder:
    """
    Класс для обработки сигналов инкрементального энкодера.
    Использует pigpio для прерываний.
    """

    def __init__(
        self,
        clk_pin: int = 5,
        dt_pin: int = 6,
        callback: Optional[Callable[[int], None]] = None,
        initial_value: int = 0
    ):
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self._value = initial_value
        self._lock = threading.Lock()
        self._callbacks = []
        self._running = True

        self.pi = pigpio.pi()
        self.pi.set_mode(clk_pin, pigpio.INPUT)
        self.pi.set_pull_up_down(clk_pin, pigpio.PUD_UP)
        self.pi.set_mode(dt_pin, pigpio.INPUT)
        self.pi.set_pull_up_down(dt_pin, pigpio.PUD_UP)

        self._last_clk = self.pi.read(clk_pin)
        self._last_dt = self.pi.read(dt_pin)

        if callback:
            self.add_callback(callback)

        # Слушаем оба пина на прерывания
        self._cb_clk = self.pi.callback(clk_pin, pigpio.EITHER_EDGE, self._isr)
        self._cb_dt = self.pi.callback(dt_pin, pigpio.EITHER_EDGE, self._isr)
    
    def _isr(self, gpio, level, tick) -> None:
        """Прерывание - вызывается при изменении любого пина."""
        if not self._running:
            return

        clk = self.pi.read(self.clk_pin)
        dt = self.pi.read(self.dt_pin)

        # Восходящий фронт первого пина → смотрим второй
        if clk == 1 and self._last_clk == 0:
            if dt == 0:
                self._change_value(1)
            else:
                self._change_value(-1)

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
        try:
            self._cb_clk.cancel()
            self._cb_dt.cancel()
        except:
            pass
        # Не вызываем pi.stop() — pigpiod общий для всех
    
    def __enter__(self):
        """Контекстный менеджер: вход."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер: выход."""
        self.stop()
        return False


# Для совместимости
IncrementalEncoder = Encoder

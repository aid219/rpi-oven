#!/usr/bin/env python3
"""
SPI FPS Test - измеряет РЕАЛЬНЫЙ FPS дисплея
"""

import os
os.environ['KIVY_VIDEO'] = 'gl'
os.environ['KIVY_LOG_LEVEL'] = 'error'

from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import time

class FPSTest(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = 'FPS Test'
        self.font_size = 40
        self.frame_times = []
        self.last_frame_time = time.time()
        self.counter = 0
        self.fps_display = 0
        
        # Рисуем цветной квадрат для визуального теста
        with self.canvas.before:
            Color(1, 0, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        Clock.schedule_interval(self.update_fps, 0)
        
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        
    def update_fps(self, dt):
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        if frame_time > 0:
            instant_fps = 1.0 / frame_time
            self.frame_times.append(instant_fps)
            if len(self.frame_times) > 60:
                self.frame_times.pop(0)
            
            self.counter += 1
            if self.counter >= 30:  # Каждые 0.5 сек
                avg_fps = sum(self.frame_times) / len(self.frame_times)
                min_fps = min(self.frame_times)
                max_fps = max(self.frame_times)
                print(f"REAL FPS: {avg_fps:.1f} (min:{min_fps:.1f}, max:{max_fps:.1f})")
                self.text = f'FPS: {avg_fps:.1f}'
                self.counter = 0
        
        # Мигаем цветом для визуального теста
        self.counter += 1
        if self.counter % 30 == 0:
            with self.canvas.before:
                Color(1 if self.counter % 60 < 30 else 0, 0, 0, 1)
                self.rect.pos = self.rect.pos
                self.rect.size = self.rect.size
        
        return True

class FPSTestApp(App):
    def build(self):
        self.title = 'SPI FPS Test'
        return FPSTest()

if __name__ == '__main__':
    FPSTestApp().run()

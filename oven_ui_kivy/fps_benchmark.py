#!/usr/bin/env python3
"""
FPS Benchmark для Kivy UI
"""

import os
os.environ['KIVY_VIDEO'] = 'gl'
os.environ['KIVY_LOG_LEVEL'] = 'warning'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle


class FPSMonitor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.fps_history = []
        
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)
        
        self.label = Label(
            text='FPS: --',
            font_size=dp(48),
            bold=True,
            color=(1, 1, 0, 1)
        )
        self.add_widget(self.label)
        
        self.info = Label(
            text='',
            font_size=dp(16),
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(self.info)
        
        # Запуск замера через 1 секунду после старта
        Clock.schedule_once(self.start_fps_monitor, 1)
        
    def _update_bg(self, instance, value):
        self.bg.size = self.size
        self.bg.pos = self.pos
        
    def start_fps_monitor(self, dt):
        Clock.schedule_interval(self.update_fps, 0.5)
        
    def update_fps(self, dt):
        fps = Clock.get_fps()
        self.fps_history.append(fps)
        
        # Средний FPS за последние 10 замеров
        if len(self.fps_history) > 10:
            self.fps_history.pop(0)
        
        avg_fps = sum(self.fps_history) / len(self.fps_history)
        
        # Цвет в зависимости от FPS
        if fps >= 50:
            color = (0, 1, 0, 1)  # Зелёный
        elif fps >= 30:
            color = (1, 1, 0, 1)  # Жёлтый
        elif fps >= 20:
            color = (1, 0.5, 0, 1)  # Оранжевый
        else:
            color = (1, 0, 0, 1)  # Красный
        
        self.label.text = f'FPS: {fps:.1f}'
        self.label.color = color
        self.info.text = f'Средний: {avg_fps:.1f}\nМин: {min(self.fps_history):.1f}\nМакс: {max(self.fps_history):.1f}'
        
        return True


class FPSApp(App):
    def build(self):
        self.title = 'FPS Benchmark'
        return FPSMonitor()
    
    def on_start(self):
        print("=== FPS BENCHMARK STARTED ===")
        print("Touch screen to see FPS changes")
        print("Press ESC to exit")


if __name__ == '__main__':
    FPSApp().run()

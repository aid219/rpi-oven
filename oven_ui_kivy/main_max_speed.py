#!/usr/bin/env python3
"""
Oven UI - MAXIMUM SPEED VERSION
Минимум анимаций, максимум производительности
"""

import os
import sys
import logging

os.environ['KIVY_VIDEO'] = 'gl'
os.environ['KIVY_LOG_LEVEL'] = 'error'
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONFIG'] = '1'
os.environ['SDL_VIDEODRIVER'] = 'KMSDRM'

logging.basicConfig(level=logging.ERROR)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.config import Config
from kivy.clock import Clock

# === МАКСИМАЛЬНАЯ ОПТИМИЗАЦИЯ ===

Config.set('kivy', 'log_level', 'error')
Config.set('graphics', 'log_max_frames', '0')
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'vsync', '1')  # ВКЛЮЧАЕМ VSYNC обратно!
Config.set('graphics', 'maxfps', '60')
Config.set('graphics', 'stencil', '0')
Config.set('graphics', 'shaders', '0')  # Отключаем шейдеры
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.uix.screenmanager import NoTransition

# Упрощённые экраны
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle


class SimpleButton(Button):
    """Простая кнопка без анимаций"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.3, 0.4, 0.6, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = dp(20)


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        layout.add_widget(Label(text='OVEN CONTROL', font_size=dp(32), bold=True))
        
        btn1 = SimpleButton(text='ВИДЕО', size_hint_y=None, height=dp(60))
        btn1.bind(on_press=lambda x: setattr(self.manager, 'current', 'video'))
        layout.add_widget(btn1)
        
        btn2 = SimpleButton(text='ПАНЕЛЬ', size_hint_y=None, height=dp(60))
        btn2.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(btn2)
        
        self.add_widget(layout)


class VideoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        layout.add_widget(Label(text='ВИДЕО', font_size=dp(32), bold=True))
        layout.add_widget(Label(text='Нет видео', font_size=dp(20)))
        
        btn = SimpleButton(text='НАЗАД', size_hint_y=None, height=dp(60))
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn)
        
        self.add_widget(layout)


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        layout.add_widget(Label(text='ПАНЕЛЬ', font_size=dp(32), bold=True))
        layout.add_widget(Label(text='Температура: 25°C', font_size=dp(20)))
        layout.add_widget(Label(text='Влажность: 50%', font_size=dp(20)))
        
        btn = SimpleButton(text='НАЗАД', size_hint_y=None, height=dp(60))
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn)
        
        self.add_widget(layout)


class FPSMonitor:
    def __init__(self):
        self.fps_history = []
        self.log_counter = 0
        
    def update(self, dt):
        fps = Clock.get_fps()
        self.fps_history.append(fps)
        if len(self.fps_history) > 60:
            self.fps_history.pop(0)
        
        self.log_counter += 1
        if self.log_counter >= 60:  # Каждую секунду
            avg = sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0
            logging.error(f"FPS: {fps:.1f} avg:{avg:.1f}")
            self.log_counter = 0
        return True


class OvenApp(App):
    def build(self):
        self.title = 'Oven MAX SPEED'
        self.fps_monitor = FPSMonitor()
        
        self.sm = ScreenManager()
        self.sm.transition = NoTransition()  # НОЛЬ анимации
        
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(VideoScreen(name='video'))
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        
        return self.sm
    
    def on_start(self):
        logging.error("=== MAX SPEED VERSION STARTED ===")
        Clock.schedule_interval(self.fps_monitor.update, 0)


if __name__ == '__main__':
    OvenApp().run()

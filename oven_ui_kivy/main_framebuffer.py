#!/usr/bin/env python3
"""
Oven UI - FRAMEBUFFER DIRECT VERSION
Прямая запись во framebuffer для максимального FPS
"""

import os
import sys
import logging

# Kivy с framebuffer
os.environ['KIVY_VIDEO'] = 'gl'
os.environ['KIVY_LOG_LEVEL'] = 'warning'
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONFIG'] = '1'

# ПРИНУДИТЕЛЬНО используем framebuffer
os.environ['SDL_VIDEODRIVER'] = 'KMSDRM'
os.environ['KMSDRM_VIDEO'] = '1'

logging.basicConfig(level=logging.WARNING)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock

# === МАКСИМАЛЬНАЯ ПРОИЗВОДИТЕЛЬНОСТЬ ===

Config.set('kivy', 'log_level', 'warning')
Config.set('graphics', 'log_max_frames', '0')
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'fullscreen', 'auto')

# Отключаем vsync для большей скорости
Config.set('graphics', 'vsync', '0')  # ОТКЛЮЧИТЬ VSYNC!
Config.set('graphics', 'maxfps', '0')  # Без ограничений

# Отключаем лишнее
Config.set('graphics', 'stencil', '0')
Config.set('graphics', 'double_tap_duration', '0')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from screens.main_screen import MainScreen
from screens.video_screen import VideoScreen
from screens.dashboard_screen import DashboardScreen


class FPSMonitor:
    def __init__(self):
        self.fps_history = []
        
    def update(self, dt):
        fps = Clock.get_fps()
        if fps < 0.1:
            return True
        self.fps_history.append(fps)
        if len(self.fps_history) > 60:
            self.fps_history.pop(0)
        if len(self.fps_history) > 10:
            avg = sum(self.fps_history) / len(self.fps_history)
            if len(self.fps_history) % 30 == 0:  # Каждые 0.5 сек
                logging.info(f"FPS: {fps:.1f} (avg:{avg:.1f})")
        return True


class OvenScreenManager(ScreenManager):
    def on_transition_complete(self, *args):
        if hasattr(self, 'current_screen') and self.current_screen:
            self.current_screen.canvas.ask_update()


class OvenApp(App):
    def build(self):
        self.title = 'Oven Control FB'
        self.fps_monitor = FPSMonitor()
        
        self.sm = OvenScreenManager()
        # Быстрые переходы
        self.sm.transition = FadeTransition(duration=0.2)
        
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(VideoScreen(name='video'))
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        
        return self.sm
    
    def on_start(self):
        logging.info("Oven App FB started (NO VSYNC)")
        Clock.schedule_interval(self.fps_monitor.update, 0)
        
    def on_stop(self):
        logging.info("Oven App stopped")


if __name__ == '__main__':
    OvenApp().run()

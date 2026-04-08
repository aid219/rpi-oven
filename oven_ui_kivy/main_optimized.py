#!/usr/bin/env python3
"""
Oven UI - Kivy Application
OPTIMIZED VERSION - Higher FPS
"""

import os
import sys
import logging

# Настройка переменных окружения ДЛЯ ОПТИМИЗАЦИИ
os.environ['KIVY_VIDEO'] = 'ffpyplayer'
os.environ['KIVY_LOG_LEVEL'] = 'warning'
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONFIG'] = '1'  # Не читать config.ini для скорости

# Настройка логирования
logging.basicConfig(level=logging.WARNING)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock

# === КРИТИЧЕСКИЕ НАСТРОЙКИ ПРОИЗВОДИТЕЛЬНОСТИ ===

# 1. Отключаем ненужные функции
Config.set('kivy', 'log_level', 'warning')
Config.set('graphics', 'log_max_frames', '0')  # Отключить логирование кадров

# 2. Размер окна и буферизация
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'double_tap_duration', '0')  # Отключаем double-tap для скорости
Config.set('graphics', 'double_tap_distance', '0')

# Включаем double buffering явно
Config.set('graphics', 'stencil', '0')  # Отключаем stencil buffer (не нужен)

# 3. Отключаем mouse multitouch (если не нужен)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# 4. Максимальный FPS и синхронизация
Config.set('graphics', 'maxfps', '0')  # Без ограничения (60 для дисплея)
Config.set('graphics', 'vsync', '1')  # ВКЛЮЧИТЬ vsync для плавности

# 5. Отключаем vsync для меньшего input lag (раскомментировать если нужно)
# Config.set('graphics', 'vsync', '0')

# 6. Используем SDL2 напрямую
os.environ['SDL_VIDEODRIVER'] = 'KMSDRM'

# 7. Плавная анимация - используем физический FPS
Clock._max_fps = 0  # Без искусственного ограничения

from screens.main_screen import MainScreen
from screens.video_screen_v2 import VideoScreen
from screens.dashboard_screen_v2 import DashboardScreen
from screens.settings_screen import SettingsScreen


class OvenScreenManager(ScreenManager):
    """Менеджер экранов с МИНИМАЛЬНЫМИ артефактами"""
    
    def on_touch_move(self, touch):
        """Плавная прокрутка при движении пальца"""
        if hasattr(self, 'current_screen'):
            touch.ud['screen_scrolling'] = True
        return super().on_touch_move(touch)
    
    def on_transition_complete(self, *args):
        """После перехода - форсируем полную перерисовку"""
        # Это убирает артефакты "кусков" после перехода
        if hasattr(self, 'current_screen') and self.current_screen:
            self.current_screen.canvas.ask_update()


class OvenApp(App):
    """Оптимизированное приложение"""
    
    def build(self):
        self.title = 'Oven Control'

        # Создаём менеджер экранов
        self.sm = OvenScreenManager()
        # Эффект перехода - FadeTransition (плавное затухание)
        # Варианты: SlideTransition, FadeTransition, SwapTransition, NoTransition
        self.sm.transition = FadeTransition(duration=0.3)
        
        # Добавляем экраны
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(VideoScreen(name='video'))
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        
        return self.sm
    
    def on_start(self):
        """При запуске"""
        logging.info("Oven App started (optimized)")

    def on_stop(self):
        logging.info("Oven App stopped")


if __name__ == '__main__':
    OvenApp().run()

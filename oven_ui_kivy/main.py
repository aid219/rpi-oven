#!/usr/bin/env python3
"""
Oven UI - Kivy Application
Современный интерфейс с видео и анимациями
"""

import os
import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Настройка переменных окружения для Kivy
os.environ['KIVY_VIDEO'] = 'gl'
os.environ['KIVY_LOG_LEVEL'] = 'info'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition, FadeTransition
from kivy.core.window import Window
from kivy.config import Config

# Настройка окна
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'fullscreen', 'auto')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'log_level', 'info')

# Обработка ошибок
def handle_exception(exc_type, exc_value, exc_traceback):
    """Глобальный обработчик исключений"""
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

from screens.main_screen import MainScreen
from screens.video_screen import VideoScreen
from screens.dashboard_screen import DashboardScreen


class OvenScreenManager(ScreenManager):
    """Менеджер экранов с анимированными переходами"""
    pass


class OvenApp(App):
    """Основное приложение"""
    
    def build(self):
        self.title = 'Oven Control'
        self.icon = 'assets/images/icon.png'
        
        # Создаём менеджер экранов
        sm = OvenScreenManager()
        
        # Добавляем экраны
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(VideoScreen(name='video'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        
        return sm
    
    def on_start(self):
        """Вызывается при запуске приложения"""
        print("Oven App started!")
        
    def on_stop(self):
        """Вызывается при остановке приложения"""
        print("Oven App stopped!")


if __name__ == '__main__':
    OvenApp().run()

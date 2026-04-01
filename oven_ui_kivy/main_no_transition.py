#!/usr/bin/env python3
"""
Oven UI - NO TRANSITION VERSION
Для SPI дисплеев - без анимации переходов
"""

import os
import sys
import logging

os.environ['KIVY_VIDEO'] = 'gl'
os.environ['KIVY_LOG_LEVEL'] = 'warning'
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONFIG'] = '1'

logging.basicConfig(level=logging.WARNING)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock

# Настройки
Config.set('kivy', 'log_level', 'warning')
Config.set('graphics', 'log_max_frames', '0')
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'vsync', '1')
Config.set('graphics', 'maxfps', '0')
Config.set('graphics', 'stencil', '0')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

os.environ['SDL_VIDEODRIVER'] = 'KMSDRM'

from screens.main_screen import MainScreen
from screens.video_screen import VideoScreen
from screens.dashboard_screen import DashboardScreen


class OvenScreenManager(ScreenManager):
    """Менеджер экранов без артефактов"""
    
    def on_transition_complete(self, *args):
        """Форсируем полную перерисовку после перехода"""
        if hasattr(self, 'current_screen') and self.current_screen:
            self.current_screen.canvas.ask_update()
            # Дополнительная перерисовка через кадр
            Clock.schedule_once(self._force_redraw, 0.016)
    
    def _force_redraw(self, dt):
        if hasattr(self, 'current_screen') and self.current_screen:
            self.current_screen.canvas.ask_update()


class OvenApp(App):
    def build(self):
        self.title = 'Oven Control'
        
        self.sm = OvenScreenManager()
        # НОЛЬ анимации - мгновенный переход
        self.sm.transition = NoTransition()
        
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(VideoScreen(name='video'))
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        
        return self.sm

    def on_start(self):
        logging.info("Oven App started (NO TRANSITION)")


if __name__ == '__main__':
    OvenApp().run()

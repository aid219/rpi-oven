#!/usr/bin/env python3
import os
import sys
import logging

os.environ['KIVY_LOG_LEVEL'] = 'info'
os.environ['KIVY_NO_ARGS'] = '1'

from kivy.config import Config
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'fullscreen', '0')    # 0 = стабильное окно. Позже сменишь на 1
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'vsync', '0')        # 0 = предотвращает черный экран на DRM
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
# hidinput ЗАКОММЕНТИРОВАН. SDL2 сам подхватит тач. Он главная причина черных экранов
# Config.set('input', 'touch', 'hidinput,/dev/input/event5')
Config.write()

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.clock import Clock

from screens.main_screen import MainScreen
from screens.video_screen_v2 import VideoScreen
from screens.dashboard_screen_v2 import DashboardScreen
from screens.settings_screen import SettingsScreen
from screens.main_wait_screen import MainWaitScreen
from encoder_handler import EncoderHandler

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class OvenApp(App):
    def build(self):
        self.encoder_handler = EncoderHandler(clk_pin=5, dt_pin=6)
        self.sm = ScreenManager(transition=FadeTransition(duration=0.2))
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(VideoScreen(name='video'))
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(MainWaitScreen(name='some'))
        
        # 🔥 ЭНКОДЕР ИНИЦИАЛИЗИРУЕМ ТОЛЬКО ПОСЛЕ ОТРИСОВКИ ПЕРВОГО КАДРА
        Clock.schedule_once(self._init_encoder_late, 0.5)
        return self.sm

    def _init_encoder_late(self, dt):
        logger.info("Инициализация энкодера в фоне...")
        self.encoder_handler.start(on_ready_callback=self._on_encoder_ready)

    def _on_encoder_ready(self, success):
        if success:
            logger.info("✅ Энкодер готов")
            for screen in self.sm.screens:
                if hasattr(screen, 'set_encoder_handler'):
                    screen.set_encoder_handler(self.encoder_handler)
        else:
            logger.error(f"❌ Ошибка энкодера: {self.encoder_handler.init_error}")

    def on_stop(self):
        if hasattr(self, 'encoder_handler'):
            self.encoder_handler.stop()


if __name__ == '__main__':
    OvenApp().run()
"""
Main Wait Screen - Главный экран с навигацией
"""
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.core.text import LabelBase

_fonts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts')
_font_path = os.path.join(_fonts_dir, 'MOSCOW2024.otf')
_FONT_NAME = 'Roboto'
if os.path.exists(_font_path):
    try:
        LabelBase.register(name='moscow', fn_regular=_font_path)
        _FONT_NAME = 'moscow'
    except Exception:
        pass


class MainWaitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer_minutes = 0
        self.timer_seconds = 0
        self.encoder_handler = None
        self.build_ui()

    def set_encoder_handler(self, handler):
        """Только сохраняем ссылку. Регистрация в on_enter"""
        self.encoder_handler = handler

    def build_ui(self):
        layout = FloatLayout()

        bg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images', '2_Frame 20.png')
        if os.path.exists(bg_path):
            layout.add_widget(Image(source=bg_path, size_hint=(1, 1), allow_stretch=True, keep_ratio=False))

        digit_w = dp(45)
        timer_row = BoxLayout(
            orientation='horizontal', size_hint=(None, None),
            size=(digit_w * 4 + dp(30), dp(90)),
            pos_hint={'center_x': 0.5, 'center_y': 0.66}, spacing=0
        )

        self.digit_m1 = Label(font_name=_FONT_NAME, font_size=dp(96), bold=True, color=(1, 1, 1, 1), text='0')
        self.digit_m2 = Label(font_name=_FONT_NAME, font_size=dp(96), bold=True, color=(1, 1, 1, 1), text='0')
        self.space = Label(font_name=_FONT_NAME, font_size=dp(96), bold=True, color=(1, 1, 1, 1), text='  ')
        self.digit_s1 = Label(font_name=_FONT_NAME, font_size=dp(96), bold=True, color=(1, 1, 1, 1), text='0')
        self.digit_s2 = Label(font_name=_FONT_NAME, font_size=dp(96), bold=True, color=(1, 1, 1, 1), text='0')

        for d in [self.digit_m1, self.digit_m2, self.digit_s1, self.digit_s2]:
            d.size_hint_x = None
            d.width = digit_w
            d.halign = 'center'
            d.valign = 'middle'
        self.space.size_hint_x = None
        self.space.width = dp(30)

        for w in [self.digit_m1, self.digit_m2, self.space, self.digit_s1, self.digit_s2]:
            timer_row.add_widget(w)
        layout.add_widget(timer_row)

        btn = Button(
            text='', size_hint=(None, None), size=(dp(130), dp(130)),
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            background_color=(0, 0, 0, 0), background_normal=''
        )
        btn.bind(on_press=self.go_to_settings)
        layout.add_widget(btn)
        self.add_widget(layout)

    def update_timer(self, minutes, seconds):
        self.digit_m1.text = str(minutes // 10)
        self.digit_m2.text = str(minutes % 10)
        self.digit_s1.text = str(seconds // 10)
        self.digit_s2.text = str(seconds % 10)

    def go_to_settings(self, instance):
        if self.manager:
            self.manager.current = 'settings'

    def _on_encoder_change(self, current_value, delta):
        self.timer_seconds += delta
        if self.timer_seconds < 0:
            self.timer_seconds = 99
            self.timer_minutes -= 1
        elif self.timer_seconds >= 100:
            self.timer_seconds = 0
            self.timer_minutes += 1
        self.timer_minutes = max(0, min(99, self.timer_minutes))
        self.timer_seconds = max(0, min(99, self.timer_seconds))
        self.update_timer(self.timer_minutes, self.timer_seconds)

    def on_enter(self):
        """При входе на экран: сброс, регистрация callback"""
        self.timer_minutes = 0
        self.timer_seconds = 0
        self.update_timer(0, 0)
        
        if self.encoder_handler:
            self.encoder_handler.reset()
            self.encoder_handler.add_callback(self._on_encoder_change)  # 🔑 ВОССТАНАВЛИВАЕМ

    def on_leave(self):
        """При выходе: убираем callback, чтобы не реагировал в фоне"""
        if self.encoder_handler:
            self.encoder_handler.remove_callback(self._on_encoder_change)
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

from encoder_timer_control import EncoderTimerControl

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
        self.button_handler = None
        self.door_switch_handler = None
        self.door_switch_active = None
        self.timer_control = EncoderTimerControl()
        self.door_overlay = None
        self.build_ui()

    def set_encoder_handler(self, handler):
        """Только сохраняем ссылку. Регистрация в on_enter"""
        self.encoder_handler = handler

    def set_button_handler(self, handler):
        """Только сохраняем ссылку. Регистрация в on_enter"""
        self.button_handler = handler

    def set_door_switch_handler(self, handler):
        """Только сохраняем ссылку. Регистрация в on_enter"""
        self.door_switch_handler = handler

    def build_ui(self):
        layout = FloatLayout()

        bg_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'assets',
            'images',
            '2_Frame 20.png'
        )
        if os.path.exists(bg_path):
            layout.add_widget(
                Image(
                    source=bg_path,
                    size_hint=(1, 1),
                    allow_stretch=True,
                    keep_ratio=False
                )
            )

        digit_w = dp(52)
        digit_gap = dp(24)
        digit_spacing = dp(4)
        digit_font_size = dp(88)
        timer_row = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(digit_w * 4 + digit_gap + digit_spacing * 4, dp(90)),
            pos_hint={'center_x': 0.5, 'center_y': 0.66},
            spacing=digit_spacing
        )

        self.digit_m1 = Label(
            font_name=_FONT_NAME,
            font_size=digit_font_size,
            bold=True,
            color=(1, 1, 1, 1),
            text='0'
        )
        self.digit_m2 = Label(
            font_name=_FONT_NAME,
            font_size=digit_font_size,
            bold=True,
            color=(1, 1, 1, 1),
            text='0'
        )
        self.space = Label(
            font_name=_FONT_NAME,
            font_size=digit_font_size,
            bold=True,
            color=(1, 1, 1, 1),
            text=''
        )
        self.digit_s1 = Label(
            font_name=_FONT_NAME,
            font_size=digit_font_size,
            bold=True,
            color=(1, 1, 1, 1),
            text='0'
        )
        self.digit_s2 = Label(
            font_name=_FONT_NAME,
            font_size=digit_font_size,
            bold=True,
            color=(1, 1, 1, 1),
            text='0'
        )

        for d in [self.digit_m1, self.digit_m2, self.digit_s1, self.digit_s2]:
            d.size_hint_x = None
            d.width = digit_w
            d.halign = 'center'
            d.valign = 'middle'

        self.space.size_hint_x = None
        self.space.width = digit_gap

        for w in [self.digit_m1, self.digit_m2, self.space, self.digit_s1, self.digit_s2]:
            timer_row.add_widget(w)

        layout.add_widget(timer_row)

        btn = Button(
            text='',
            size_hint=(None, None),
            size=(dp(130), dp(130)),
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            background_color=(0, 0, 0, 0),
            background_normal=''
        )
        btn.bind(on_press=self.go_to_settings)
        layout.add_widget(btn)

        door_img_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'assets',
            'images',
            'door_open.png'
        )

        self.door_overlay = Image(
            source=door_img_path,
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=False,
            opacity=0
        )
        layout.add_widget(self.door_overlay)

        self.add_widget(layout)

    def update_timer(self, minutes, seconds):
        self.digit_m1.text = str(minutes // 10)
        self.digit_m2.text = str(minutes % 10)
        self.digit_s1.text = str(seconds // 10)
        self.digit_s2.text = str(seconds % 10)

    def go_to_settings(self, instance=None):
        if self.manager:
            self.manager.current = 'settings'

    def _show_door_overlay(self, show):
        if self.door_overlay is not None:
            self.door_overlay.opacity = 1 if show else 0

    def _on_encoder_change(self, current_value, delta):
        self.timer_minutes, self.timer_seconds = self.timer_control.apply_delta(
            self.timer_minutes,
            self.timer_seconds,
            delta,
        )
        self.update_timer(self.timer_minutes, self.timer_seconds)

    def on_enter(self):
        """При входе на экран: сброс, регистрация callback"""
        self.timer_minutes = 0
        self.timer_seconds = 0
        self.timer_control.reset_motion()
        self.update_timer(0, 0)

        if self.encoder_handler:
            self.encoder_handler.reset()
            self.encoder_handler.add_callback(self._on_encoder_change)

        if self.button_handler:
            self.button_handler.add_callback(self._on_encoder_button_press)

        if self.door_switch_handler:
            self.door_switch_active = self.door_switch_handler.is_active()
            self._show_door_overlay(bool(self.door_switch_active))
            self.door_switch_handler.add_callback(self._on_door_switch_change)
        else:
            self._show_door_overlay(False)

    def on_leave(self):
        """При выходе: убираем callback, чтобы не реагировал в фоне"""
        if self.encoder_handler:
            self.encoder_handler.remove_callback(self._on_encoder_change)

        if self.button_handler:
            self.button_handler.remove_callback(self._on_encoder_button_press)

        if self.door_switch_handler:
            self.door_switch_handler.remove_callback(self._on_door_switch_change)

    def _on_encoder_button_press(self):
        self.go_to_settings()

    def _on_door_switch_change(self, is_active):
        self.door_switch_active = is_active
        self._show_door_overlay(is_active)
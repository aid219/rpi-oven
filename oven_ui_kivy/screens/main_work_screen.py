"""
Main Screen - Главный экран с навигацией
"""

from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle


class AnimatedButton(Button):
    """Анимированная кнопка с эффектами"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.2, 0.3, 0.5, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = dp(18)
        self.border_radius = [dp(10)]
        
        # Градиентный фон через canvas
        with self.canvas.before:
            Color(0.2, 0.3, 0.5, 1)
            self.rect = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[dp(10)]
            )
        
        self.bind(size=self._update_rect, pos=self._update_rect)
        
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Анимация нажатия
            anim = Animation(background_color=(0.4, 0.5, 0.7, 1), duration=0.1)
            anim.start(self)
            return super().on_touch_down(touch)
        return False
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            # Возврат к исходному цвету
            anim = Animation(background_color=(0.2, 0.3, 0.5, 1), duration=0.2)
            anim.start(self)
            return super().on_touch_up(touch)
        return False


class MainScreen(Screen):
    """Главный экран меню"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        """Построение интерфейса"""
        layout = FloatLayout()
        
        # Заголовок
        title = Label(
            text='OVEN CONTROL',
            font_size=dp(32),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.15),
            pos_hint={'top': 1}
        )
        layout.add_widget(title)
        

        btn_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint=(0.9, 0.6),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        settings_btn = AnimatedButton(
            text='SETTINGS',
            size_hint_y=0.25
        )
        settings_btn.bind(on_press=self.go_to_settings)
        btn_layout.add_widget(settings_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
           
    def go_to_settings(self, instance):
        """Переход в настройки"""
        if self.manager:
            self.manager.current = 'settings'

 


# KV-разметка для фона
from kivy.lang import Builder

Builder.load_string('''
<MainScreen>:
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.2, 1
        Rectangle:
            pos: self.pos
            size: self.size
''')

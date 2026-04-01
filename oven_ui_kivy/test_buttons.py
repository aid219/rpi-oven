#!/usr/bin/env python3
"""
Тест кнопок и переходов между экранами
"""

import os
os.environ['KIVY_LOG_LEVEL'] = 'debug'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp


class TestButton(Button):
    """Кнопка для теста"""
    
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.size_hint_y = None
        self.height = dp(60)
        self.background_normal = ''
        self.background_color = (0.2, 0.4, 0.6, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = dp(20)
        self.bind(on_press=self.on_button_press)
        
    def on_button_press(self, instance):
        print(f"Button pressed: {self.text}")
        instance.background_color = (0.4, 0.6, 0.8, 1)
        
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.background_color = (0.2, 0.4, 0.6, 1)
            return super().on_touch_up(touch)
        return False


class TestScreen(BoxLayout):
    """Тестовый экран"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(15)
        
        # Заголовок
        self.add_widget(Label(
            text='TEST TOUCH SCREEN',
            font_size=dp(24),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        ))
        
        # Кнопки
        for i in range(5):
            btn = TestButton(text=f'Button {i+1}')
            self.add_widget(btn)
        
        # Инфо
        self.add_widget(Label(
            text='Нажимайте кнопки мышью или тачскрином',
            font_size=dp(14),
            size_hint_y=None,
            height=dp(40)
        ))


class TestApp(App):
    def build(self):
        self.title = 'Touch Test'
        return TestScreen()
    
    def on_start(self):
        print("Test app started!")
        print("Touch the buttons to test")


if __name__ == '__main__':
    TestApp().run()

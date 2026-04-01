"""
Settings Screen - Системная регулировка яркости
Через /sys/class/backlight/backlight_gpio/brightness
"""

from kivy.uix.screenmanager import Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.metrics import dp
import os


class SettingsScreen(Screen):
    """Экран настроек с системной яркостью"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brightness_slider = None
        self.brightness_label = None
        self.backlight_path = '/sys/class/backlight/backlight_gpio/brightness'
        self.max_brightness = 1  # По умолчанию 2 состояния
        self.current_value = 1
        
        # Проверяем доступность
        self.check_backlight()
        self.build_ui()
        
    def check_backlight(self):
        """Проверить backlight и max_brightness"""
        if os.path.exists(self.backlight_path):
            max_path = self.backlight_path.replace('brightness', 'max_brightness')
            try:
                with open(max_path, 'r') as f:
                    self.max_brightness = int(f.read().strip())
                print(f"Backlight found: {self.backlight_path}, max={self.max_brightness}")
            except:
                self.max_brightness = 1
        else:
            print(f"Backlight not found at {self.backlight_path}")
            self.backlight_path = None
            
    def build_ui(self):
        """Вертикальная компоновка"""
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(15)
        )
        
        # 1. Заголовок
        title = Label(
            text='SETTINGS',
            font_size=dp(28),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(title)
        
        # 2. Яркость экрана
        brightness_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(180),
            padding=dp(10)
        )
        
        with brightness_box.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.25, 0.25, 0.35, 0.9)
            brightness_box.rect = RoundedRectangle(
                size=brightness_box.size,
                pos=brightness_box.pos,
                radius=[dp(15)]
            )
        brightness_box.bind(
            size=lambda i,v: setattr(brightness_box.rect, 'size', v),
            pos=lambda i,v: setattr(brightness_box.rect, 'pos', v)
        )
        
        # Заголовок яркости
        brightness_box.add_widget(Label(
            text='BRIGHTNESS',
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40)
        ))
        
        # Значение яркости
        self.brightness_label = Label(
            text='100%',
            font_size=dp(40),
            bold=True,
            size_hint_y=None,
            height=dp(60)
        )
        brightness_box.add_widget(self.brightness_label)
        
        # Слайдер яркости
        self.brightness_slider = Slider(
            min=0,
            max=100,
            value=100,
            size_hint_y=None,
            height=dp(50)
        )
        self.brightness_slider.bind(value=self.on_brightness_change)
        brightness_box.add_widget(self.brightness_slider)
        
        main_layout.add_widget(brightness_box)
        
        # 3. Информация
        info_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120)
        )
        
        info_box.add_widget(Label(
            text='Display Settings',
            font_size=dp(18),
            size_hint_y=None,
            height=dp(35)
        ))
        
        info_box.add_widget(Label(
            text=f'Path: {self.backlight_path or "N/A"}',
            font_size=dp(12),
            size_hint_y=None,
            height=dp(30)
        ))
        
        info_box.add_widget(Label(
            text=f'Max: {self.max_brightness}',
            font_size=dp(14),
            size_hint_y=None,
            height=dp(30)
        ))
        
        if self.max_brightness == 1:
            info_box.add_widget(Label(
                text='⚠️ Only ON/OFF supported',
                font_size=dp(14),
                color=(1, 0.5, 0, 1),
                size_hint_y=None,
                height=dp(30)
            ))
        
        main_layout.add_widget(info_box)
        
        # 4. Кнопка НАЗАД
        back_btn = Button(
            text='BACK',
            font_size=dp(24),
            bold=True,
            size_hint_y=None,
            height=dp(60)
        )
        back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(back_btn)
        
        self.add_widget(main_layout)
        
    def on_brightness_change(self, instance, value):
        """Изменение яркости через sysfs"""
        percent = int(value)
        
        # Обновить текст
        if self.brightness_label:
            self.brightness_label.text = f'{percent}%'
        
        # Установить яркость
        self.set_brightness(percent)
        
    def set_brightness(self, percent):
        """Установить яркость через sysfs"""
        if not self.backlight_path:
            print(f"Backlight not available")
            return
            
        try:
            # Конвертировать процент в значение (0 или 1)
            if self.max_brightness == 1:
                value = 1 if percent >= 50 else 0
            else:
                value = int((percent / 100.0) * self.max_brightness)
            
            # Записать в sysfs
            with open(self.backlight_path, 'w') as f:
                f.write(str(value))
            
            self.current_value = value
            print(f"Brightness: {percent}% → {value}/{self.max_brightness}")
        except Exception as e:
            print(f"Error setting brightness: {e}")
            
    def go_back(self, instance):
        """Назад в главное меню - сохраняем яркость"""
        print(f"Leaving settings, brightness={self.current_value}")
        # Отключаем обработчик
        if self.brightness_slider:
            self.brightness_slider.unbind(value=self.on_brightness_change)
        self.manager.transition = FadeTransition(duration=0.3)
        self.manager.current = 'main'
        
    def on_leave(self):
        """При уходе - НЕ меняем яркость"""
        pass


# Фон экрана
from kivy.lang import Builder

Builder.load_string('''
<SettingsScreen>:
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.15, 1
        Rectangle:
            pos: self.pos
            size: self.size
''')

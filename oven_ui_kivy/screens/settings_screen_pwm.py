"""
Settings Screen - Настройки с PWM регулировкой яркости
Прямое управление GPIO 18 (PWM)
"""

from kivy.uix.screenmanager import Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.metrics import dp
import os

# Импортируем RPi.GPIO
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


class SettingsScreen(Screen):
    """Экран настроек с PWM яркостью"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brightness_slider = None
        self.brightness_label = None
        self.pwm = None
        self.brightness_pin = 18  # GPIO 18 = PWM0
        self.pwm_frequency = 1000  # 1 kHz
        self.current_duty = 50  # 50% по умолчанию
        
        # Инициализация GPIO
        if GPIO_AVAILABLE:
            self.setup_gpio()
        
        self.build_ui()
        
    def setup_gpio(self):
        """Настройка GPIO и PWM"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.brightness_pin, GPIO.OUT)
            
            # Инициализация PWM
            self.pwm = GPIO.PWM(self.brightness_pin, self.pwm_frequency)
            self.pwm.start(self.current_duty)
            print(f"PWM initialized on GPIO{self.brightness_pin} at {self.pwm_frequency}Hz")
        except Exception as e:
            print(f"GPIO setup error: {e}")
            self.pwm = None
            
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
        
        # Значение яркости (%)
        self.brightness_label = Label(
            text='50%',
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
            value=50,
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
            text=f'PWM Pin: GPIO{self.brightness_pin}',
            font_size=dp(14),
            size_hint_y=None,
            height=dp(30)
        ))
        
        info_box.add_widget(Label(
            text=f'Frequency: {self.pwm_frequency} Hz',
            font_size=dp(14),
            size_hint_y=None,
            height=dp(30)
        ))
        
        info_box.add_widget(Label(
            text=f'GPIO Available: {GPIO_AVAILABLE}',
            font_size=dp(14),
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
        """Изменение яркости через PWM"""
        duty_cycle = int(value)
        
        # Обновить текст
        if self.brightness_label:
            self.brightness_label.text = f'{duty_cycle}%'
        
        # Установить PWM
        self.set_pwm_duty(duty_cycle)
        
    def set_pwm_duty(self, duty):
        """Установить duty cycle PWM"""
        if self.pwm:
            try:
                self.pwm.ChangeDutyCycle(duty)
                self.current_duty = duty
                print(f"Brightness: {duty}% (PWM duty cycle)")
            except Exception as e:
                print(f"PWM error: {e}")
        else:
            print(f"PWM not available, GPIO available: {GPIO_AVAILABLE}")
            
    def go_back(self, instance):
        """Назад в главное меню - оставляем текущую яркость"""
        print(f"Leaving settings, brightness stays at {self.current_duty}%")
        # Отключаем обработчик чтобы не было мерцания
        self.brightness_slider.unbind(value=self.on_brightness_change)
        self.manager.transition = FadeTransition(duration=0.3)
        self.manager.current = 'main'
        
    def on_leave(self):
        """При уходе с экрана - НЕ меняем яркость"""
        pass  # Оставляем последнюю установленную яркость
        
    def on_stop(self):
        """Только при полном закрытии приложения - 100% яркость"""
        # Устанавливаем 100% и НЕ останавливаем PWM
        if self.pwm:
            self.pwm.ChangeDutyCycle(100)
            print("APP CLOSED - Brightness set to 100% (PWM still running)")
            # НЕ вызываем pwm.stop() и НЕ вызываем GPIO.cleanup()
            # Оставляем PWM работать на 100%
        else:
            # Если PWM не доступен, включаем напрямую
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(18, GPIO.OUT)
            GPIO.output(18, GPIO.HIGH)
            print("APP CLOSED - GPIO 18 set to HIGH")


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

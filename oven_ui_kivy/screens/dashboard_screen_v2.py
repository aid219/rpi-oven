"""
Dashboard Screen - НА ВЕСЬ ЭКРАН БЕЗ СКРОЛЛА
Исправлены артефакты шрифтов
"""

from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle
from kivy.properties import NumericProperty, ListProperty


class CircularProgress(Widget):
    """Круговой индикатор"""
    
    value = NumericProperty(0)
    max = NumericProperty(100)
    color = ListProperty([0, 1, 0, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pending_update = False
        self.bind(size=self._schedule_update, pos=self._schedule_update)
        self.bind(value=self._schedule_update, max=self._schedule_update, color=self._schedule_update)
        Clock.schedule_once(self._update)
        
    def _schedule_update(self, *args):
        if not self._pending_update:
            self._pending_update = True
            Clock.schedule_once(self._do_update, 0.05)
        
    def _do_update(self, dt):
        self._update()
        self._pending_update = False
        
    def _update(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*self.color)
            Color(0.3, 0.3, 0.3, 1)
            center_x = self.center_x
            center_y = self.center_y
            radius = min(self.width, self.height) / 2 - dp(5)
            Ellipse(pos=(center_x - radius, center_y - radius), size=(radius * 2, radius * 2))
            Color(*self.color)
            if self.value > 0:
                angle = 360 * (self.value / self.max)
                Line(circle=(center_x, center_y, radius, 0, angle), width=dp(8))


class DashboardScreen(Screen):
    """Панель управления - НА ВЕСЬ ЭКРАН"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temperature = 25
        self.humidity = 50
        self.temp_value_label = None
        self.humid_value_label = None
        self.build_ui()
        
    def build_ui(self):
        """Вертикальная компоновка на весь экран"""
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )
        
        # 1. Заголовок
        title = Label(
            text='DASHBOARD',
            font_size=dp(28),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        main_layout.add_widget(title)
        
        # 2. Карточки с показателями (2 в ряд)
        cards_layout = GridLayout(
            cols=2,
            size_hint_y=None,
            height=dp(120),
            spacing=dp(10)
        )
        
        # Температура
        self.temp_card = self.create_card("TEMP", "25 C", (1, 0.3, 0, 1))
        cards_layout.add_widget(self.temp_card)
        
        # Влажность
        self.humid_card = self.create_card("HUMID", "50 %", (0, 0.5, 1, 1))
        cards_layout.add_widget(self.humid_card)
        
        main_layout.add_widget(cards_layout)
        
        # 3. Круговые индикаторы (2 в ряд)
        progress_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(140),
            spacing=dp(15)
        )
        
        # Индикатор температуры
        temp_box = BoxLayout(orientation='vertical')
        temp_box.add_widget(Label(
            text="TEMP",
            size_hint_y=None,
            height=dp(30)
        ))
        self.temp_progress = CircularProgress(
            value=25,
            max=100,
            color=[1, 0.3, 0, 1],
            size_hint_y=1
        )
        temp_box.add_widget(self.temp_progress)
        progress_layout.add_widget(temp_box)
        
        # Индикатор влажности
        humid_box = BoxLayout(orientation='vertical')
        humid_box.add_widget(Label(
            text="HUMID",
            size_hint_y=None,
            height=dp(30)
        ))
        self.humid_progress = CircularProgress(
            value=50,
            max=100,
            color=[0, 0.5, 1, 1],
            size_hint_y=1
        )
        humid_box.add_widget(self.humid_progress)
        progress_layout.add_widget(humid_box)
        
        main_layout.add_widget(progress_layout)
        
        # 4. Слайдеры управления
        control_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(130),
            spacing=dp(15),
            padding=dp(10)
        )
        
        # Слайдер температуры
        temp_slider_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50)
        )
        temp_slider_box.add_widget(Label(
            text="TEMP",
            size_hint_x=None,
            width=dp(70)
        ))
        self.temp_slider = Slider(
            min=0,
            max=100,
            value=25,
            size_hint_x=1
        )
        self.temp_slider.bind(value=self.on_temp_change)
        temp_slider_box.add_widget(self.temp_slider)
        control_layout.add_widget(temp_slider_box)
        
        # Слайдер влажности
        humid_slider_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50)
        )
        humid_slider_box.add_widget(Label(
            text="HUMID",
            size_hint_x=None,
            width=dp(70)
        ))
        self.humid_slider = Slider(
            min=0,
            max=100,
            value=50,
            size_hint_x=1
        )
        self.humid_slider.bind(value=self.on_humid_change)
        humid_slider_box.add_widget(self.humid_slider)
        control_layout.add_widget(humid_slider_box)
        
        main_layout.add_widget(control_layout)
        
        # 5. Кнопка НАЗАД
        back_btn = Button(
            text='BACK',
            font_size=dp(24),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(back_btn)
        
        self.add_widget(main_layout)
        
    def create_card(self, title, value, color):
        """Создать карточку показателя"""
        card = BoxLayout(orientation='vertical', padding=dp(5))
        
        with card.canvas.before:
            Color(0.25, 0.25, 0.35, 0.9)
            card.rect = RoundedRectangle(
                size=card.size,
                pos=card.pos,
                radius=[dp(10)]
            )
        card.bind(size=lambda i,v: setattr(card.rect, 'size', v),
                  pos=lambda i,v: setattr(card.rect, 'pos', v))
        
        # Заголовок карточки
        title_label = Label(
            text=title,
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(title_label)
        
        # Значение (это будем обновлять)
        value_label = Label(
            text=value,
            font_size=dp(24),
            bold=True,
            size_hint_y=1
        )
        card.add_widget(value_label)
        
        return card  # Возвращаем всю карточку, value_label это children[1]
        
    def on_temp_change(self, instance, value):
        self.temperature = int(value)
        self.temp_progress.value = value
        # children[0] = value_label (крупный шрифт, последний добавлен)
        if hasattr(self, 'temp_card') and len(self.temp_card.children) > 0:
            self.temp_card.children[0].text = f"{int(value)} C"
        
    def on_humid_change(self, instance, value):
        self.humidity = int(value)
        self.humid_progress.value = value
        # children[0] = value_label (крупный шрифт, последний добавлен)
        if hasattr(self, 'humid_card') and len(self.humid_card.children) > 0:
            self.humid_card.children[0].text = f"{int(value)} %"
        
    def go_back(self, instance):
        """Назад в главное меню"""
        if self.manager:
            self.manager.current = 'main'


# Фон экрана
from kivy.lang import Builder

Builder.load_string('''
<DashboardScreen>:
    canvas.before:
        Color:
            rgba: 0.1, 0.15, 0.2, 1
        Rectangle:
            pos: self.pos
            size: self.size
''')

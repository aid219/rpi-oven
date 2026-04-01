"""
Dashboard Screen - Панель управления с виджетами
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Ellipse, RoundedRectangle, Line
from kivy.properties import NumericProperty, ListProperty


class CircularProgress(Widget):
    """Круговой индикатор прогресса - ОПТИМИЗИРОВАННЫЙ"""
    
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
        """Отложенное обновление для производительности"""
        if not self._pending_update:
            self._pending_update = True
            Clock.schedule_once(self._do_update, 0.05)  # 20 FPS для индикаторов
        
    def _do_update(self, dt):
        """Реальное обновление canvas"""
        self._update()
        self._pending_update = False
        
    def _update(self, *args):
        """Обновление canvas"""
        self.canvas.clear()
        with self.canvas:
            Color(*self.color)
            
            # Фон (круг)
            Color(0.3, 0.3, 0.3, 1)
            center_x = self.center_x
            center_y = self.center_y
            radius = min(self.width, self.height) / 2 - dp(5)
            Ellipse(pos=(center_x - radius, center_y - radius), size=(radius * 2, radius * 2))
            
            # Прогресс (дуга)
            Color(*self.color)
            if self.value > 0:
                angle = 360 * (self.value / self.max)
                Line(circle=(center_x, center_y, radius, 0, angle), width=dp(8))


class AnimatedSlider(Slider):
    """Слайдер с анимацией"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(40)
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Анимация увеличения при нажатии
            anim = Animation(height=dp(50), duration=0.1)
            anim.start(self)
            return super().on_touch_down(touch)
        return False
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(height=dp(40), duration=0.2)
            anim.start(self)
            return super().on_touch_up(touch)
        return False


class DashboardCard(BoxLayout):
    """Карточка с информацией"""
    
    def __init__(self, title="", value="", unit="", icon="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(5)
        
        # Фон карточки
        with self.canvas.before:
            Color(0.25, 0.25, 0.35, 0.9)
            self.rect = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[dp(15)]
            )
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # Иконка
        icon_label = Label(
            text=icon,
            font_size=dp(32),
            size_hint_y=None,
            height=dp(40)
        )
        self.add_widget(icon_label)
        
        # Заголовок
        title_label = Label(
            text=title,
            font_size=dp(14),
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=dp(25)
        )
        self.add_widget(title_label)
        
        # Значение
        value_label = Label(
            text=f"{value}{unit}",
            font_size=dp(24),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(35)
        )
        self.add_widget(value_label)
        
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class DashboardScreen(Screen):
    """Панель управления"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        self.temperature = 25  # Начальная температура
        self.humidity = 50     # Начальная влажность
        
    def build_ui(self):
        """Построение интерфейса"""
        from kivy.uix.scrollview import ScrollView
        
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(10),
            spacing=dp(15)
        )
        layout.bind(minimum_height=layout.setter('height'))
        
        # Заголовок
        title = Label(
            text='DASHBOARD',
            font_size=dp(24),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # Карточки с показателями
        cards_layout = GridLayout(
            cols=2,
            size_hint_y=None,
            height=dp(180),
            spacing=dp(10)
        )
        
        # Температура
        self.temp_card = DashboardCard(
            title="Temperature",
            value="25",
            unit="C",
            icon=""
        )
        cards_layout.add_widget(self.temp_card)
        
        # Влажность
        self.humid_card = DashboardCard(
            title="Humidity",
            value="50",
            unit="%",
            icon=""
        )
        cards_layout.add_widget(self.humid_card)
        
        layout.add_widget(cards_layout)
        
        # Круговые индикаторы
        progress_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(150),
            spacing=dp(20),
            padding=dp(10)
        )
        
        # Индикатор температуры
        temp_progress_box = BoxLayout(orientation='vertical')
        temp_progress_box.add_widget(Label(
            text="Нагрев",
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=dp(30)
        ))
        self.temp_progress = CircularProgress(
            value=25,
            max=100,
            color=[1, 0.3, 0, 1],
            size_hint_y=None,
            height=dp(100)
        )
        temp_progress_box.add_widget(self.temp_progress)
        progress_layout.add_widget(temp_progress_box)
        
        # Индикатор влажности
        humid_progress_box = BoxLayout(orientation='vertical')
        humid_progress_box.add_widget(Label(
            text="Влажность",
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=dp(30)
        ))
        self.humid_progress = CircularProgress(
            value=50,
            max=100,
            color=[0, 0.5, 1, 1],
            size_hint_y=None,
            height=dp(100)
        )
        humid_progress_box.add_widget(self.humid_progress)
        progress_layout.add_widget(humid_progress_box)
        
        layout.add_widget(progress_layout)
        
        # Слайдеры управления
        control_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(150),
            spacing=dp(10),
            padding=dp(10)
        )
        
        control_layout.add_widget(Label(
            text="Управление",
            font_size=dp(18),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(30)
        ))
        
        # Слайдер температуры
        temp_slider_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50)
        )
        temp_slider_layout.add_widget(Label(
            text="TEMP",
            font_size=dp(18),
            size_hint_x=None,
            width=dp(60)
        ))
        self.temp_slider = AnimatedSlider(
            min=0,
            max=100,
            value=25
        )
        self.temp_slider.bind(value=self.on_temp_change)
        temp_slider_layout.add_widget(self.temp_slider)
        control_layout.add_widget(temp_slider_layout)
        
        # Слайдер влажности
        humid_slider_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50)
        )
        humid_slider_layout.add_widget(Label(
            text="HUMID",
            font_size=dp(18),
            size_hint_x=None,
            width=dp(60)
        ))
        self.humid_slider = AnimatedSlider(
            min=0,
            max=100,
            value=50
        )
        self.humid_slider.bind(value=self.on_humid_change)
        humid_slider_layout.add_widget(self.humid_slider)
        control_layout.add_widget(humid_slider_layout)
        
        layout.add_widget(control_layout)
        
        # Кнопка назад
        back_btn = Button(
            text='← На главную',
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.3, 0.3, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size=dp(18)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        scroll.add_widget(layout)
        self.add_widget(scroll)
        
        # Обновление показателей
        Clock.schedule_interval(self.update_indicators, 1)
        
    def on_temp_change(self, instance, value):
        """Изменение температуры"""
        self.temperature = int(value)
        self.temp_progress.value = value
        self.temp_card.children[0].text = f"{int(value)}°C"
        
    def on_humid_change(self, instance, value):
        """Изменение влажности"""
        self.humidity = int(value)
        self.humid_progress.value = value
        self.humid_card.children[0].text = f"{int(value)}%"
        
    def update_indicators(self, dt):
        """Периодическое обновление индикаторов"""
        # Здесь можно добавить чтение реальных датчиков
        pass
        
    def go_back(self, instance):
        """Возврат на главный экран"""
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'


from kivy.uix.screenmanager import SlideTransition
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

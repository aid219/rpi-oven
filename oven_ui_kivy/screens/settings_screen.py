"""
Settings Screen - Настройки приложения
- Выбор темы (светлая/тёмная)
- Выбор типа перехода между экранами
"""

from kivy.uix.screenmanager import Screen, FadeTransition, SlideTransition, SwapTransition, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.properties import StringProperty


class SettingsScreen(Screen):
    """Экран настроек"""
    
    # Текущие настройки
    current_theme = StringProperty('Dark')
    current_transition = StringProperty('Fade')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
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
        
        # 2. Выбор темы
        theme_box = self._create_setting_box(
            title='THEME',
            values=['Dark', 'Light'],
            current=self.current_theme,
            on_select=self.on_theme_select
        )
        main_layout.add_widget(theme_box)
        
        # 3. Выбор перехода
        transition_box = self._create_setting_box(
            title='TRANSITION',
            values=['Fade', 'Slide', 'Swap', 'None'],
            current=self.current_transition,
            on_select=self.on_transition_select
        )
        main_layout.add_widget(transition_box)
        
        # 4. Информация
        info_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100)
        )
        
        info_box.add_widget(Label(
            text='Application Settings',
            font_size=dp(18),
            size_hint_y=None,
            height=dp(35)
        ))
        
        info_box.add_widget(Label(
            text='Changes apply immediately',
            font_size=dp(14),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=dp(30)
        ))
        
        main_layout.add_widget(info_box)
        
        # 5. Кнопка НАЗАД
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
        
    def _create_setting_box(self, title, values, current, on_select):
        """Создать блок настройки"""
        box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=dp(10)
        )
        
        with box.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.25, 0.25, 0.35, 0.9)
            box.rect = RoundedRectangle(
                size=box.size,
                pos=box.pos,
                radius=[dp(15)]
            )
        box.bind(
            size=lambda i,v: setattr(box.rect, 'size', v),
            pos=lambda i,v: setattr(box.rect, 'pos', v)
        )
        
        # Заголовок
        box.add_widget(Label(
            text=title,
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40)
        ))
        
        # Spinner для выбора
        spinner = Spinner(
            text=current,
            values=values,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18)
        )
        spinner.bind(text=on_select)
        box.add_widget(spinner)
        
        return box
        
    def on_theme_select(self, spinner, value):
        """Выбор темы"""
        self.current_theme = value
        print(f"Theme selected: {value}")
        # Здесь можно применить тему
        # self.apply_theme(value)
        
    def on_transition_select(self, spinner, value):
        """Выбор типа перехода"""
        self.current_transition = value
        print(f"Transition selected: {value}")
        
        # Применить переход ГЛОБАЛЬНО для всех экранов
        if self.manager:
            self._apply_transition(value)
            
    def _apply_transition(self, value):
        """Применить тип перехода"""
        if value == 'Fade':
            new_transition = FadeTransition(duration=0.3)
        elif value == 'Slide':
            new_transition = SlideTransition(duration=0.3)
        elif value == 'Swap':
            new_transition = SwapTransition(duration=0.3)
        elif value == 'None':
            new_transition = NoTransition()
        else:
            new_transition = FadeTransition(duration=0.3)
            
        # Применить ко всем экранам
        self.manager.transition = new_transition
        
        # Обновить все экраны
        for screen in self.manager.screens:
            if hasattr(screen, 'manager'):
                screen.manager.transition = new_transition
                
    def go_back(self, instance):
        """Назад в главное меню"""
        self._apply_transition(self.current_transition)
        self.manager.current = 'main'


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

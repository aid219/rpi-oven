"""
Video Screen - Экран воспроизведения видео
FIXED VERSION - кнопки не накладываются
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
from kivy.core.window import Window

# Пробуем импортировать Video
try:
    from kivy.uix.video import Video
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False


class ControlButton(Button):
    """Кнопка управления"""
    
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.background_normal = ''
        self.background_color = (0.3, 0.3, 0.4, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = dp(20)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(50)


class VideoWindow(FloatLayout):
    """Окно для видео"""
    
    def __init__(self, video_path=None, title="Video", **kwargs):
        super().__init__(**kwargs)
        self.video_path = video_path
        self.title = title
        self.video = None
        self.build_ui()
        
    def build_ui(self):
        """Построение интерфейса"""
        # Главный контейнер
        main_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1)
        )
        
        # 1. Видео контейнер (верхняя часть)
        video_box = BoxLayout(
            size_hint_y=None,
            height=self.height * 0.75  # 75% экрана под видео
        )
        
        if self.video_path and VIDEO_AVAILABLE:
            try:
                self.video = Video(
                    source=self.video_path,
                    size_hint=(1, 1),
                    state='stop'
                )
                video_box.add_widget(self.video)
            except Exception as e:
                print(f"Video error: {e}")
                video_box.add_widget(Label(text='Video Error', font_size=dp(20)))
        else:
            video_box.add_widget(Label(
                text='No Video',
                font_size=dp(32)
            ))
        
        main_layout.add_widget(video_box)
        
        # 2. Панель управления (нижняя часть)
        control_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=self.height * 0.25,  # 25% экрана под кнопки
            spacing=dp(10),
            padding=dp(10)
        )
        
        # Кнопка PLAY
        self.play_btn = ControlButton(text='PLAY')
        self.play_btn.bind(on_press=self.toggle_play)
        control_box.add_widget(self.play_btn)
        
        # Кнопка STOP
        stop_btn = ControlButton(text='STOP')
        stop_btn.bind(on_press=self.stop_video)
        control_box.add_widget(stop_btn)
        
        # Кнопка BACK
        back_btn = ControlButton(text='BACK')
        back_btn.bind(on_press=self.go_back)
        control_box.add_widget(back_btn)
        
        main_layout.add_widget(control_box)
        
        self.add_widget(main_layout)
        
    def toggle_play(self, instance):
        """Play/Pause"""
        if self.video:
            if self.video.state == 'play':
                self.video.state = 'pause'
                self.play_btn.text = 'PLAY'
            else:
                self.video.state = 'play'
                self.play_btn.text = 'PAUSE'
                
    def stop_video(self, instance):
        """Stop"""
        if self.video:
            self.video.state = 'stop'
            self.play_btn.text = 'PLAY'
            
    def go_back(self, instance):
        """Назад"""
        if self.parent and hasattr(self.parent, 'parent'):
            self.parent.parent.transition = SlideTransition(direction='right')
            self.parent.parent.current = 'main'


class VideoScreen(Screen):
    """Экран с видео"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        """Построение интерфейса"""
        # Заголовок
        title = Label(
            text='VIDEO',
            font_size=dp(28),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.1),
            pos_hint={'top': 1}
        )
        self.add_widget(title)
        
        # Видео окно (под заголовком)
        video_window = VideoWindow(
            video_path="assets/videos/1.mp4",
            title="Main Video",
            size_hint=(1, 0.9),
            pos_hint={'top': 0.9}
        )
        self.add_widget(video_window)
        
    def on_enter(self):
        print("Video screen entered")
        
    def on_leave(self):
        if VIDEO_AVAILABLE:
            for widget in self.walk():
                if isinstance(widget, Video):
                    widget.state = 'stop'


# KV-разметка для фона
from kivy.lang import Builder

Builder.load_string('''
<VideoScreen>:
    canvas.before:
        Color:
            rgba: 0.15, 0.1, 0.2, 1
        Rectangle:
            pos: self.pos
            size: self.size
''')

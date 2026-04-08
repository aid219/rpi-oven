"""
Video Screen - FIXED VERSION 2
Видео сверху, кнопки снизу
"""

from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp

try:
    from kivy.uix.video import Video
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False


class VideoScreen(Screen):
    """Экран с видео"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video = None
        self.build_ui()
        
    def build_ui(self):
        """Вертикальная компоновка"""
        # Главный контейнер - вертикальный
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )
        
        # 1. Заголовок
        title = Label(
            text='VIDEO',
            font_size=dp(28),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        main_layout.add_widget(title)
        
        # 2. Видео (занимает доступное место)
        video_box = BoxLayout()

        try:
            self.video = Video(
                source="assets/videos/1.mp4",
                size_hint=(1, 1),
                state='stop'
            )
            video_box.add_widget(self.video)
        except Exception as e:
            print(f"Video error: {e}")
            video_box.add_widget(Label(text='No Video', font_size=dp(32)))
            self.video = None

        main_layout.add_widget(video_box)

        # 3. Кнопки (3 равные кнопки в ряд)
        buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10)
        )

        # PLAY
        self.play_btn = Button(
            text='PLAY',
            font_size=dp(24),
            bold=True
        )
        self.play_btn.bind(on_press=self.toggle_play)
        buttons_layout.add_widget(self.play_btn)

        # STOP
        stop_btn = Button(
            text='STOP',
            font_size=dp(24),
            bold=True
        )
        stop_btn.bind(on_press=self.stop_video)
        buttons_layout.add_widget(stop_btn)
        
        # BACK
        back_btn = Button(
            text='BACK',
            font_size=dp(24),
            bold=True
        )
        back_btn.bind(on_press=self.go_back)
        buttons_layout.add_widget(back_btn)
        
        main_layout.add_widget(buttons_layout)
        
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
        if self.manager:
            self.manager.current = 'main'
        
    def on_leave(self):
        """Остановить видео при уходе с экрана"""
        if self.video:
            self.video.state = 'stop'


# Фон экрана
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

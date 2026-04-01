"""
Video Screen - Экран воспроизведения видео
Работает даже без доступного видео-провайдера
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

# Пробуем импортировать Video, но не ломаем если нет
try:
    from kivy.uix.video import Video
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False
    Video = object  # Заглушка


class ControlButton(Button):
    """Кнопка управления с анимацией"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.3, 0.3, 0.4, 0.9)
        self.color = (1, 1, 1, 1)
        self.font_size = dp(24)
        self.bold = True
        self.border_radius = [dp(10)]
        self.size_hint_y = None
        self.height = dp(60)
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(background_color=(0.5, 0.5, 0.7, 1), duration=0.1)
            anim.start(self)
            return super().on_touch_down(touch)
        return False
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(background_color=(0.3, 0.3, 0.4, 0.9), duration=0.2)
            anim.start(self)
            return super().on_touch_up(touch)
        return False


class VideoWindow(FloatLayout):
    """Окно для воспроизведения видео"""
    
    def __init__(self, video_path=None, title="Video", **kwargs):
        super().__init__(**kwargs)
        self.video_path = video_path
        self.title = title
        self.video = None
        self.build_ui()
        
    def build_ui(self):
        """Построение интерфейса окна"""
        # Контейнер для видео
        video_container = BoxLayout(
            size_hint=(1, None),
            height=dp(320),
            pos_hint={'top': 1}
        )
        
        # Пробуем загрузить видео
        if self.video_path:
            try:
                from kivy.uix.video import Video
                self.video = Video(
                    source=self.video_path,
                    size_hint=(1, 1),
                    state='stop'
                )
                video_container.add_widget(self.video)
            except Exception as e:
                print(f"Video error: {e}")
                self._add_placeholder(video_container)
        else:
            self._add_placeholder(video_container)
        
        self.add_widget(video_container)
        
        # Панель управления
        control_panel = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.15),
            pos_hint={'bottom': 0},
            spacing=dp(15),
            padding=dp(15)
        )
        
        # Кнопка Play/Pause
        self.play_btn = ControlButton(text='PLAY')
        self.play_btn.size_hint_x = 1
        if self.video:
            self.play_btn.bind(on_press=self.toggle_play)
        else:
            self.play_btn.disabled = True
        control_panel.add_widget(self.play_btn)
        
        # Кнопка Stop
        stop_btn = ControlButton(text='STOP')
        stop_btn.size_hint_x = 1
        if self.video:
            stop_btn.bind(on_press=self.stop_video)
        else:
            stop_btn.disabled = True
        control_panel.add_widget(stop_btn)
        
        # Кнопка Назад
        back_btn = ControlButton(text='BACK')
        back_btn.size_hint_x = 1
        back_btn.bind(on_press=self.go_back)
        control_panel.add_widget(back_btn)
        
        self.add_widget(control_panel)
    
    def _add_placeholder(self, container):
        """Заглушка если видео не доступно"""
        placeholder = BoxLayout(orientation='vertical')
        placeholder.add_widget(Label(text='No Video', font_size=dp(32)))
        container.add_widget(placeholder)
        
    def toggle_play(self, instance):
        """Переключение play/pause"""
        if self.video:
            if self.video.state == 'play':
                self.video.state = 'pause'
                self.play_btn.text = '▶'
            else:
                self.video.state = 'play'
                self.play_btn.text = '⏸'
                
    def stop_video(self, instance):
        """Остановка видео"""
        if self.video:
            self.video.state = 'stop'
            self.video.position = 0
            self.play_btn.text = '▶'
            
    def go_back(self, instance):
        """Возврат на главный экран"""
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
        from kivy.uix.scrollview import ScrollView
        
        # Скролл для нескольких видео окон
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
            text='ВИДЕО',
            font_size=dp(28),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # Видео окно 1
        video_window1 = VideoWindow(
            video_path="assets/videos/1.mp4",  # Путь к видео файлу
            title="Основное видео",
            size_hint_y=None,
            height=dp(300)
        )
        layout.add_widget(video_window1)
        
        # Видео окно 2 (заглушка)
        video_window2 = VideoWindow(
            video_path=None,
            title="Дополнительное видео",
            size_hint_y=None,
            height=dp(200)
        )
        layout.add_widget(video_window2)
        
        scroll.add_widget(layout)
        self.add_widget(scroll)
        
    def on_enter(self):
        """Вызывается при переходе на экран"""
        print("Video screen entered")
        
    def on_leave(self):
        """Вызывается при уходе с экрана"""
        # Останавливаем все видео при уходе
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

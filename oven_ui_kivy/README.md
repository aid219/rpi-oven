# Kivy UI для Oven Control

Современный интерфейс управления с видео и анимациями на базе Kivy.

## 📋 Возможности

- ✅ Современный Material Design интерфейс
- ✅ Анимированные переходы между экранами
- ✅ Анимированные кнопки с эффектами
- ✅ Поддержка видео (при наличии кодеков)
- ✅ Панель управления с виджетами
- ✅ Поддержка мультитача
- ✅ Адаптация под 320x480 дисплей

## 🚀 Установка

### 1. Установка зависимостей

```bash
# Системные зависимости
sudo apt-get update
sudo apt-get install -y python3-pip \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libgl1-mesa-dri libgbm-dev libgstreamer1.0-dev \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    libmtdev-dev xclip xsel

# Kivy и зависимости
pip3 install --break-system-packages --no-cache-dir \
    kivy \
    filetype \
    docutils \
    pygments \
    Kivy-Garden
```

### 2. Запуск

```bash
cd /home/qummy/rpi-oven/oven_ui_kivy

# Через скрипт
bash run.sh

# Или напрямую
python3 main.py
```

## 📁 Структура проекта

```
oven_ui_kivy/
├── main.py                 # Точка входа
├── run.sh                  # Скрипт запуска
├── screens/
│   ├── __init__.py
│   ├── main_screen.py      # Главный экран (меню)
│   ├── video_screen.py     # Экран видео
│   └── dashboard_screen.py # Панель управления
├── widgets/
│   └── __init__.py
└── assets/
    ├── videos/             # Видео файлы
    └── images/             # Изображения
```

## 🎮 Управление

### Главный экран
- **Видео** - переход на экран с видео
- **Панель управления** - датчики и управление
- **Настройки** - заглушка

### Видео экран
- **▶/⏸** - Play/Pause
- **⏹** - Stop
- **← Назад** - возврат в главное меню

### Панель управления
- 🌡️ **Температура** - слайдер и индикатор
- 💧 **Влажность** - слайдер и индикатор
- **← На главную** - возврат в главное меню

## 🎨 Особенности

### Анимации
- Плавные переходы между экранами (Slide/Fade)
- Анимированные кнопки (нажатие, наведение)
- Частицы на фоне главного экрана
- Круговые индикаторы прогресса

### Видео
- Поддержка форматов: MP4, AVI, WebM (зависит от кодеков)
- Для работы видео нужен GStreamer
- При отсутствии видео-провайдера показывается заглушка

### Тачскрин
- Автоматическое определение устройства
- Поддержка мультитача
- Координаты: 0-319 (X), 0-479 (Y)

## 🔧 Настройка

### Добавить видео
Поместите видеофайл в `/home/qummy/rpi-oven/oven_ui_kivy/assets/videos/`

Измените в `screens/video_screen.py`:
```python
video_window1 = VideoWindow(
    video_path="assets/videos/my_video.mp4",  # Путь к видео
    ...
)
```

### Изменить разрешение
В `main.py`:
```python
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '480')
```

### Сменить тему
Отредактируйте цвета в `canvas.before` каждого экрана.

## 📊 Производительность

- **FPS:** ~25-30 (аппаратное ускорение OpenGL ES 2)
- **Запуск:** < 2 секунд
- **Память:** ~50-80 MB

## ⚠️ Известные проблемы

1. **Видео не работает** - отсутствует GStreamer или кодеки
   - Решение: `sudo apt-get install gstreamer1.0-plugins-good gstreamer1.0-plugins-bad`

2. **Тачскрин не калиброван** - координаты не совпадают
   - Решение: настроить в `/boot/firmware/overlays/ft6336u-fix.dtbo`

3. **Низкий FPS** - проверьте, что используется аппаратное ускорение
   - Проверка: `glxinfo | grep "OpenGL version"`

## 📝 Логи

Логи Kivy сохраняются в: `/home/qummy/.kivy/logs/`

Просмотр в реальном времени:
```bash
tail -f /home/qummy/.kivy/logs/kivy_*.txt
```

## 🔗 Ссылки

- [Документация Kivy](https://kivy.org/doc/stable/)
- [Kivy на Raspberry Pi](https://kivy.org/doc/stable/installation/installation-rpi.html)
- [GStreamer для видео](https://gstreamer.freedesktop.org/)

---

**Создано:** 2026-04-01
**Версия:** 1.0.0

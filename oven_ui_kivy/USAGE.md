# 🎯 Kivy UI - Инструкция по использованию

## ✅ Статус
Приложение работает! Кнопки нажимаются, переходы между экранами работают.

---

## 🚀 Быстрый запуск

```bash
cd /home/qummy/rpi-oven/oven_ui_kivy
python3 main.py
```

Или через скрипт:
```bash
bash run.sh
```

---

## 📱 Как использовать

### Главный экран
Нажимайте кнопки:
- **🎬 Видео** — переход на экран видео
- **📊 Панель управления** — датчики и слайдеры
- **⚙️ Настройки** — заглушка (в разработке)

### Видео экран
- Кнопки управления неактивны (нет видеофайла)
- Кнопка **← Назад** возвращает в главное меню

### Панель управления
- Двигайте слайдеры 🌡️ и 💧
- Индикаторы обновляются в реальном времени
- Кнопка **← На главную** возвращает назад

---

## 🔧 Тестирование тачскрина

### Тест 1: Простой тест кнопок
```bash
cd /home/qummy/rpi-oven/oven_ui_kivy
python3 test_buttons.py
```
Нажимайте на 5 кнопок по очереди.

### Тест 2: Проверка координат тачскрина
```bash
sudo evtest /dev/input/event3
```
Коснитесь экрана — должны видеть события с координатами.

---

## ⚠️ Известные ограничения

### 1. Видео не работает
**Сообщение:** `[CRITICAL] [Video] Unable to find any valuable Video provider`

**Причина:** Не установлены кодеки GStreamer

**Решение (если нужно видео):**
```bash
sudo apt-get install gstreamer1.0-plugins-good gstreamer1.0-plugins-bad
pip3 install --break-system-packages gstplayer
```

**Временное решение:** Использовать заглушки (уже реализовано)

---

## 📊 Логи

### Просмотр логов Kivy
```bash
# Последние логи
tail -f /home/qummy/.kivy/logs/kivy_*.txt

# Или все логи
ls -la /home/qummy/.kivy/logs/
```

### Логи в реальном времени
```bash
# Запуск с логированием
cd /home/qummy/rpi-oven/oven_ui_kivy
python3 main.py 2>&1 | tee app.log
```

---

## 🐛 Отладка

### Если приложение падает:

1. **Проверьте логи:**
   ```bash
   cat /home/qummy/.kivy/logs/kivy_*.txt | tail -100
   ```

2. **Запустите с отладкой:**
   ```bash
   python3 -c "
   import os
   os.environ['KIVY_LOG_LEVEL'] = 'debug'
   from main import OvenApp
   OvenApp().run()
   "
   ```

3. **Проверьте тачскрин:**
   ```bash
   sudo evtest /dev/input/event3
   ```

### Если кнопки не нажимаются:

1. **Проверьте координаты:**
   ```bash
   sudo evtest /dev/input/event3
   # Коснитесь экрана, проверьте координаты
   # Должны быть: X=0-319, Y=0-479
   ```

2. **Тест кнопок:**
   ```bash
   python3 test_buttons.py
   ```

---

## 📁 Структура проекта

```
oven_ui_kivy/
├── main.py              # Главный файл запуска
├── run.sh               # Скрипт быстрого запуска
├── test_buttons.py      # Тест кнопок
├── README.md            # Документация
├── screens/
│   ├── main_screen.py   # Главное меню
│   ├── video_screen.py  # Видео экран
│   └── dashboard_screen.py  # Панель управления
├── widgets/
├── assets/
│   ├── videos/          # Видео файлы (пусто)
│   └── images/          # Изображения (пусто)
└── systemd/
    ├── kivy-oven-ui.service  # Systemd сервис
    └── install-service.sh    # Установка сервиса
```

---

## 🎨 Настройка

### Изменить размер окна
В `main.py`:
```python
Config.set('graphics', 'width', '320')   # Ширина
Config.set('graphics', 'height', '480')  # Высота
```

### Изменить цвета кнопок
В `screens/main_screen.py`:
```python
self.background_color = (0.2, 0.3, 0.5, 1)  # R, G, B, Alpha
```

### Добавить видео
1. Поместите файл `.mp4` в `assets/videos/`
2. В `screens/video_screen.py` измените:
   ```python
   video_window1 = VideoWindow(
       video_path="assets/videos/my_video.mp4",
       ...
   )
   ```

---

## 📞 Поддержка

### Файлы для проверки
- `KIVY_UI_PROGRESS.md` — история разработки
- `README.md` — основная документация
- Логи: `/home/qummy/.kivy/logs/`

### Команды для диагностики
```bash
# Версия Kivy
python3 -c "import kivy; print(kivy.__version__)"

# Проверка OpenGL
glxinfo | grep "OpenGL version"

# Проверка тачскрина
ls /dev/input/event*
sudo evtest /dev/input/event3

# Проверка логов
tail -50 /home/qummy/.kivy/logs/kivy_*.txt
```

---

## ✅ Чеклист работоспособности

- [x] Kivy установлен (v2.3.1)
- [x] OpenGL ES 2.0 работает
- [x] Тачскрин определяется (/dev/input/event3)
- [x] Координаты: X=0-319, Y=0-479
- [x] Главное меню отображается
- [x] Кнопки нажимаются
- [x] Переходы между экранами работают
- [x] Видео экран показывает заглушку
- [x] Панель управления работает
- [x] Слайдеры двигаются
- [x] Индикаторы обновляются

---

**Версия:** 1.0.0  
**Дата:** 2026-04-01  
**Статус:** ✅ Работает

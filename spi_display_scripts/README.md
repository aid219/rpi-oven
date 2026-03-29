# Скрипты для SPI дисплея ST7796U

## Файлы

### `panel.bin`
**Готовый файл инициализации для ST7796U с нормальными цветами!**

Копирование:
```bash
sudo cp panel.bin /lib/firmware/panel.bin
sudo rmmod panel_mipi_dbi drm_mipi_dbi
sudo modprobe panel_mipi_dbi
```

**Важно:** Содержит команду 0x21 (Display Inversion ON) для нормальных цветов (чёрный фон, белый текст).

### `create_panel_bin.py`
Создаёт файл инициализации `panel.bin` для драйвера `panel-mipi-dbi`.

**Использование:**
```bash
python3 create_panel_bin.py
sudo cp panel.bin /lib/firmware/panel.bin
```

### `simple_spi_anim.py`
Простая анимация прыгающего мяча для теста производительности.

**Использование:**
```bash
sudo python3 simple_spi_anim.py
```

**Производительность:** ~30 FPS

### `pygame_spi_direct.py`
Анимация с прыгающим мячом, вращающимся солнцем и ракеткой. Красивая демонстрация.

**Использование:**
```bash
sudo python3 pygame_spi_direct.py
```

**Производительность:** ~30 FPS

### `demo_display.py`
Демонстрационная анимация с цветами, градиентами и эффектами.

**Использование:**
```bash
sudo python3 demo_display.py
```

### `test_fb_direct.py`
Тест прямого доступа к framebuffer с различными цветами и градиентами.

**Использование:**
```bash
sudo python3 test_fb_direct.py
```

### `play_gif*.py`
Скрипты для воспроизведения GIF анимации.

**Использование:**
```bash
sudo python3 play_gif_working.py /path/to/animation.gif
```

## Быстрый старт

1. Создать panel.bin:
```bash
python3 create_panel_bin.py
sudo cp panel.bin /lib/firmware/
```

2. Перезагрузить драйвер:
```bash
sudo rmmod panel_mipi_dbi drm_mipi_dbi
sudo modprobe panel_mipi_dbi
```

3. Запустить анимацию:
```bash
sudo python3 simple_spi_anim.py
```

## Требования

- Python 3
- Raspberry Pi OS Bookworm (64-bit)
- Ядро 6.x с модулем panel-mipi-dbi
- Настроенный SPI дисплей ST7796U

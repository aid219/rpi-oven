# Настройка SPI дисплея ST7796U 320x480 на Raspberry Pi

## Цель
Вывод консоли Linux (терминала) на IPS дисплей ST7796U 320x480 через SPI интерфейс Raspberry Pi.

## Оборудование
- **Дисплей:** ST7796U IPS 320x480 (SPI)
- **Плата:** Raspberry Pi Zero 2 W / Pi 3 / Pi 4
- **OS:** Raspberry Pi OS Bookworm (64-bit)

## Подключение пинов

| Дисплей | Raspberry Pi | GPIO | Pin # |
|---------|--------------|------|-------|
| VCC     | 3.3V         | -    | 1     |
| GND     | GND          | -    | 6     |
| CS      | GPIO8        | 8    | 24    |
| RST     | GPIO24       | 24   | 18    |
| DC      | GPIO25       | 25   | 22    |
| SDA/MOSI| GPIO10       | 10   | 19    |
| SCK     | GPIO11       | 11   | 23    |
| BLK     | GPIO18       | 18   | 12    |

**Важно:** BLK (backlight) может требовать транзистор/мосфет для управления, если дисплей потребляет больше тока чем может дать GPIO.

---

## Шаг 1: Подготовка системы

### 1.1 Обновление системы
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git device-tree-compiler
```

### 1.2 Проверка версии ядра
```bash
uname -r
# Должно быть 6.x (например, 6.12.47+rpt-rpi-v7)
```

---

## Шаг 2: Включение SPI

### 2.1 Редактирование config.txt
```bash
sudo nano /boot/firmware/config.txt
```

### 2.2 Добавить в конец файла:
```ini
dtparam=spi=on
```

### 2.3 Проверка SPI устройств
После перезагрузки:
```bash
ls /dev/spi*
# Должно показать: /dev/spidev0.0  /dev/spidev0.1
```

---

## Шаг 3: Blacklist для spidev

Модуль `spidev` конфликтует с `panel-mipi-dbi`. Нужно его отключить.

### 3.1 Создать файл blacklist
```bash
sudo nano /etc/modprobe.d/blacklist-spidev.conf
```

### 3.2 Содержимое файла:
```
blacklist spidev
```

### 3.3 Проверка что spidev не загружен
```bash
lsmod | grep spidev
# Должно быть пусто
```

---

## Шаг 4: Создание panel.bin

Драйвер `panel-mipi-dbi` требует файл инициализации `/lib/firmware/panel.bin` в специальном формате.

### 4.1 Формат panel.bin
- **Байты 0-14:** Magic "MIPI DBI" + 7 нулей (15 байт)
- **Байт 15:** Версия (0x01)
- **Байты 16+:** Команды в формате `[cmd] [len] [data...]`
- **Задержка:** команда 0x00 с 1 параметром (мс)

### 4.2 Скрипт для создания panel.bin

Создать файл `create_panel_bin.py`:

```python
#!/usr/bin/env python3
"""
Создать panel.bin в формате panel-mipi-dbi для ST7796U
ВАЖНО: Команда 0x21 (Display Inversion ON) для нормальных цветов!
"""

MAGIC = b'MIPI DBI' + b'\x00' * 7
VERSION = b'\x01'

def cmd(code, data=None):
    """Создать команду: [cmd] [len] [data...]"""
    if data is None:
        data = []
    return bytes([code, len(data)]) + bytes(data)

def delay(ms):
    """Создать задержку: NOP (0x00) с параметром задержки"""
    return bytes([0x00, 0x01, ms & 0xFF])

# ST7796U инициализация
commands = bytearray()

# Reset
commands += cmd(0x01)  # SWRESET
commands += delay(120)

# Sleep Out
commands += cmd(0x11)
commands += delay(150)

# Command 2 (Protection)
commands += cmd(0xF0, [0xC3])
commands += cmd(0xF0, [0x96])

# Interface Mode Control
commands += cmd(0x36, [0x48])  # MV=1, RGB=1

# Pixel Format
commands += cmd(0x3A, [0x55])  # 16-bit/pixel

# Frame Rate Control
commands += cmd(0xB4, [0x01])

# Display Inversion ON - ВАЖНО для нормальных цветов!
# Некоторые дисплеи инвертированы, 0x21 делает цвета нормальными
commands += cmd(0x21)

# Display Inversion Mode
commands += cmd(0xB6, [0x80, 0x02, 0x3B])

# Gate Control
commands += cmd(0xE8, [0x40, 0x8A, 0x00, 0x00, 0x29, 0x19, 0xA5, 0x33])

# Power Control 1
commands += cmd(0xC1, [0x06])

# Power Control 2
commands += cmd(0xC2, [0xA7])

# VCOM Control
commands += cmd(0xC5, [0x18])

# Positive Gamma
commands += cmd(0xE0, [0xF0, 0x09, 0x0B, 0x06, 0x04, 0x15, 0x2F, 0x54, 0x42, 0x3C, 0x17, 0x14, 0x18, 0x1B])

# Negative Gamma
commands += cmd(0xE1, [0xE0, 0x09, 0x0B, 0x06, 0x04, 0x03, 0x2B, 0x43, 0x42, 0x3B, 0x16, 0x14, 0x17, 0x1B])

# Command 2 (Disable protection)
commands += cmd(0xF0, [0x3C])
commands += cmd(0xF0, [0x69])

# Display ON
commands += cmd(0x29)

# Column Address Set
commands += cmd(0x2A, [0x00, 0x00, 0x01, 0x3F])  # 0-319

# Row Address Set
commands += cmd(0x2B, [0x00, 0x00, 0x01, 0xDF])  # 0-479

# Создаём финальный файл
firmware = MAGIC + VERSION + commands

with open('panel.bin', 'wb') as f:
    f.write(firmware)

print(f"Создан panel.bin: {len(firmware)} байт")
```

```python
#!/usr/bin/env python3
"""
Создать panel.bin в формате panel-mipi-dbi для ST7796U
"""

MAGIC = b'MIPI DBI' + b'\x00' * 7
VERSION = b'\x01'

def cmd(code, data=None):
    """Создать команду: [cmd] [len] [data...]"""
    if data is None:
        data = []
    return bytes([code, len(data)]) + bytes(data)

def delay(ms):
    """Создать задержку: NOP (0x00) с параметром задержки"""
    return bytes([0x00, 0x01, ms & 0xFF])

# ST7796U инициализация
commands = bytearray()

# Reset
commands += cmd(0x01)  # SWRESET
commands += delay(120)

# Sleep Out
commands += cmd(0x11)
commands += delay(150)

# Command 2 (Protection)
commands += cmd(0xF0, [0xC3])
commands += cmd(0xF0, [0x96])

# Interface Mode Control
commands += cmd(0x36, [0x48])  # MV=1, RGB=1

# Pixel Format
commands += cmd(0x3A, [0x55])  # 16-bit/pixel

# Frame Rate Control
commands += cmd(0xB4, [0x01])

# Display Inversion Control
commands += cmd(0xB6, [0x80, 0x02, 0x3B])

# Gate Control
commands += cmd(0xE8, [0x40, 0x8A, 0x00, 0x00, 0x29, 0x19, 0xA5, 0x33])

# Power Control 1
commands += cmd(0xC1, [0x06])

# Power Control 2
commands += cmd(0xC2, [0xA7])

# VCOM Control
commands += cmd(0xC5, [0x18])

# Positive Gamma
commands += cmd(0xE0, [0xF0, 0x09, 0x0B, 0x06, 0x04, 0x15, 0x2F, 0x54, 0x42, 0x3C, 0x17, 0x14, 0x18, 0x1B])

# Negative Gamma
commands += cmd(0xE1, [0xE0, 0x09, 0x0B, 0x06, 0x04, 0x03, 0x2B, 0x43, 0x42, 0x3B, 0x16, 0x14, 0x17, 0x1B])

# Command 2 (Disable protection)
commands += cmd(0xF0, [0x3C])
commands += cmd(0xF0, [0x69])

# Display ON
commands += cmd(0x29)

# Column Address Set
commands += cmd(0x2A, [0x00, 0x00, 0x01, 0x3F])  # 0-319

# Row Address Set
commands += cmd(0x2B, [0x00, 0x00, 0x01, 0xDF])  # 0-479

# Создаём финальный файл
firmware = MAGIC + VERSION + commands

with open('panel.bin', 'wb') as f:
    f.write(firmware)

print(f"Создан panel.bin: {len(firmware)} байт")
```

### 4.3 Запуск скрипта
```bash
python3 create_panel_bin.py
# Создан panel.bin: 117 байт
```

### 4.4 Копирование в firmware directory
```bash
sudo cp panel.bin /lib/firmware/panel.bin
sudo chmod 644 /lib/firmware/panel.bin
ls -la /lib/firmware/panel.bin
```

---

## Шаг 5: Настройка Device Tree Overlay

Используем стандартный overlay `mipi-dbi-spi` с параметрами.

### 5.1 Редактирование config.txt
```bash
sudo nano /boot/firmware/config.txt
```

### 5.2 Добавить в конец файла:
```ini
dtoverlay=mipi-dbi-spi,spi0-0,speed=62000000
dtparam=width=320,height=480
dtparam=reset-gpio=24,dc-gpio=25
dtparam=backlight-gpio=18
```

**Параметры:**
- `spi0-0` - SPI шина 0, chip select 0
- `speed=62000000` - частота SPI 62 MHz
- `width=320,height=480` - разрешение дисплея
- `reset-gpio=24` - GPIO 24 для RST
- `dc-gpio=25` - GPIO 25 для DC
- `backlight-gpio=18` - GPIO 18 для подсветки

---

## Шаг 6: Настройка консоли (fbcon)

### 6.1 Редактирование cmdline.txt
```bash
sudo nano /boot/firmware/cmdline.txt
```

### 6.2 Добавить параметры fbcon

**Оригинальная строка (пример):**
```
console=serial0,115200 console=tty1 root=PARTUUID=...
```

**Изменённая строка:**
```
console=serial0,115200 console=tty1 fbcon=map:1 fbcon=font:VGA8x16 root=PARTUUID=...
```

**Важно:** Вся строка должна быть **одной строкой** без переносов!

**Параметры:**
- `fbcon=map:1` - использовать framebuffer 1 (SPI дисплей)
- `fbcon=font:VGA8x16` - шрифт 8x16 пикселей

---

## Шаг 7: Автозагрузка модуля panel-mipi-dbi

### 7.1 Добавить модуль в /etc/modules
```bash
echo 'panel_mipi_dbi' | sudo tee -a /etc/modules
```

### 7.2 Проверка
```bash
cat /etc/modules
# Должно содержать: panel_mipi_dbi
```

---

## Шаг 8: Перезагрузка и проверка

### 8.1 Перезагрузка
```bash
sudo reboot
```

### 8.2 После перезагрузки - проверка

**Проверка framebuffer:**
```bash
ls -la /dev/fb*
# Должно показать:
# crw-rw---- 1 root video 29, 0 ... /dev/fb0
# crw-rw---- 1 root video 29, 1 ... /dev/fb1
```

**Проверка загрузки драйвера:**
```bash
dmesg | grep -iE 'mipi|panel|dbi|fb1' | tail -20
```

**Ожидаемый вывод:**
```
[   XX.XXXXXX] panel-mipi-dbi-spi spi0.0: supply power not found, using dummy regulator
[   XX.XXXXXX] panel-mipi-dbi-spi spi0.0: supply io not found, using dummy regulator
[   XX.XXXXXX] [drm] Initialized panel-mipi-dbi 1.0.0 for spi0.0 on minor 1
[   XX.XXXXXX] Console: switching to colour frame buffer device 40x30
[   XX.XXXXXX] panel-mipi-dbi-spi spi0.0: [drm] fb1: panel-mipi-dbid frame buffer device
```

**Проверка подсветки:**
```bash
ls -la /sys/class/backlight/
# Должно показать: backlight_gpio -> ../../devices/platform/backlight_gpio/...
```

**Включение подсветки:**
```bash
echo 1 | sudo tee /sys/class/backlight/backlight_gpio/brightness
```

---

## Шаг 9: Проверка работы

### 9.1 Тестовый вывод на дисплей
```bash
echo "Тест SPI дисплея" | sudo tee /dev/fb1
# Или просто посмотрите на консоль - текст должен быть на дисплее
```

### 9.2 Проверка консоли
Консоль должна отображаться на SPI дисплее с разрешением 40x30 символов.

Попробуйте:
```bash
date
uptime
ls -la
```

Текст команд и вывода должен быть виден на дисплее.

---

## Шаг 10: Управление подсветкой

### 10.1 Включить подсветку
```bash
echo 1 | sudo tee /sys/class/backlight/backlight_gpio/brightness
```

### 10.2 Выключить подсветку
```bash
echo 0 | sudo tee /sys/class/backlight/backlight_gpio/brightness
```

### 10.3 Автоматическое включение подсветки при загрузке

Создать скрипт `/etc/rc.local` (если не существует):
```bash
sudo nano /etc/rc.local
```

Содержимое:
```bash
#!/bin/bash
echo 1 > /sys/class/backlight/backlight_gpio/brightness
exit 0
```

Сделать исполняемым:
```bash
sudo chmod +x /etc/rc.local
```

---

## Диагностика проблем

### Проблема: Нет /dev/fb1

**Проверка:**
```bash
dmesg | grep -iE 'mipi|panel|spi0'
lsmod | grep mipi
```

**Решение:**
```bash
sudo modprobe panel_mipi_dbi
```

Если ошибка "Bad magic" - неверный panel.bin, пересоздать.

### Проблема: spidev конфликтует

**Проверка:**
```bash
ls /dev/spi*
# Если есть /dev/spidev0.0 - конфликт
```

**Решение:**
```bash
sudo rmmod spidev
echo 'blacklist spidev' | sudo tee /etc/modprobe.d/blacklist-spidev.conf
```

### Проблема: Консоль на HDMI, а не на SPI

**Проверка:**
```bash
cat /boot/firmware/cmdline.txt
# Должно содержать fbcon=map:1
```

**Решение:**
Добавить `fbcon=map:1` в cmdline.txt и перезагрузиться.

### Проблема: Экран чёрный, но подсветка работает

**Возможные причины:**
1. Неверный panel.bin - пересоздать
2. Неправильное подключение пинов - проверить
3. Дисплей не получает питание - проверить 3.3V

**Проверка инициализации:**
```bash
dmesg | grep 'panel-mipi-dbi'
# Не должно быть ошибок "probe failed"
```

### Проблема: Искажённое изображение

**Причины:**
1. Неправильная ориентация (параметр 0x36 в panel.bin)
2. Неправильный формат цвета (параметр 0x3A)

**Решение:** Изменить panel.bin и перезагрузить модуль:
```bash
sudo rmmod panel_mipi_dbi drm_mipi_dbi
sudo modprobe panel_mipi_dbi
```

### Проблема: Инвертированные цвета (белый фон, чёрный текст)

**Симптомы:**
- Консоль белая с чёрным текстом (должно быть наоборот)
- Изображение "негативное"

**Решение:** Добавить команду 0x21 (Display Inversion ON) в panel.bin:

```python
# В скрипт create_panel_bin.py добавить после команды 0xB4:
commands += cmd(0x21)  # Display Inversion ON - для нормальных цветов!
```

**Полная последовательность команд в panel.bin:**
```python
commands += cmd(0xB4, [0x01])  # Frame Rate Control
commands += cmd(0x21)          # Display Inversion ON - ВАЖНО!
commands += cmd(0xB6, [0x80, 0x02, 0x3B])  # Display Inversion Mode
```

**Примечание:** Некоторые ST7796U дисплеи имеют инвертированную логику цветов. 
Команда 0x21 включает инверсию, которая делает цвета нормальными (чёрный фон, белый текст).

**После изменения panel.bin:**
```bash
sudo cp panel.bin /lib/firmware/panel.bin
sudo rmmod panel_mipi_dbi drm_mipi_dbi
sudo modprobe panel_mipi_dbi
```

**Проверка:**
```bash
# Экран должен стать чёрным с белым текстом
echo "Тест цветов"
```

---

## Файлы конфигурации (итог)

### /boot/firmware/config.txt (добавить в конец):
```ini
dtparam=spi=on
dtoverlay=mipi-dbi-spi,spi0-0,speed=62000000
dtparam=width=320,height=480
dtparam=reset-gpio=24,dc-gpio=25
dtparam=backlight-gpio=18
```

### /boot/firmware/cmdline.txt (одна строка!):
```
console=serial0,115200 console=tty1 root=PARTUUID=c9164067-02 rootfstype=ext4 fsck.repair=yes rootwait cfg80211.ieee80211_regdom=RU
```

**Важно:** После настройки SPI дисплея как основного (fb0), можно добавить `fbcon=map:0`:
```
console=serial0,115200 console=tty0 fbcon=map:0 fbcon=font:VGA8x16 root=PARTUUID=c9164067-02 rootfstype=ext4 fsck.repair=yes rootwait cfg80211.ieee80211_regdom=RU
```

### /etc/modprobe.d/blacklist-spidev.conf:
```
blacklist spidev
```

### /etc/modules (добавить строку):
```
panel_mipi_dbi
```

### /lib/firmware/panel.bin:
Бинарный файл инициализации (119 байт для ST7796U с командой 0x21)

**Содержит команды:**
- 0x01 - SWRESET
- 0x11 - Sleep Out
- 0xF0 - Protection
- 0x36 - Memory Access Control (0x48)
- 0x3A - Pixel Format (0x55 = RGB565)
- 0xB4 - Frame Rate Control
- **0x21 - Display Inversion ON** (для нормальных цветов!)
- 0xB6 - Display Inversion Mode
- 0xE8, 0xC1, 0xC2, 0xC5 - Power/Gate/VCOM control
- 0xE0, 0xE1 - Gamma correction
- 0x29 - Display ON
- 0x2A, 0x2B - Resolution (320x480)

---

## Запуск pygame/анимации на SPI дисплее

### Прямой доступ к framebuffer

Создать скрипт `simple_spi_anim.py`:

```python
#!/usr/bin/env python3
import struct, fcntl, mmap, time, math

WIDTH, HEIGHT = 320, 480

def rgb565(r, g, b):
    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return bytes([color & 0xFF, (color >> 8) & 0xFF])

fb = open('/dev/fb1', 'r+b')
line_length = 640  # WIDTH * 2 для RGB565
fb_mem = mmap.mmap(fb.fileno(), line_length * HEIGHT, prot=mmap.PROT_WRITE)

def clear(color):
    line = color * WIDTH
    for y in range(HEIGHT):
        fb_mem.seek(y * line_length)
        fb_mem.write(line)

def draw_circle(cx, cy, r, color, fill=False):
    if fill:
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x-cx)**2 + (y-cy)**2 <= r**2:
                    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                        fb_mem.seek(y * line_length + x * 2)
                        fb_mem.write(color)

# Пример использования
RED = rgb565(255, 0, 0)
clear(RED)  # Очистить красным
draw_circle(160, 240, 50, rgb565(255, 255, 0), fill=True)  # Жёлтый круг

fb_mem.close()
fb.close()
```

### Запуск:
```bash
sudo python3 simple_spi_anim.py
```

**Производительность:** ~30 FPS при выводе полного кадра.

### Готовые скрипты

В папке `spi_display_scripts/` доступны:

- `simple_spi_anim.py` - простой тест FPS с прыгающим мячом
- `pygame_spi_direct.py` - красивая анимация с солнцем, мячом и ракеткой
- `demo_display.py` - демонстрация с цветами и эффектами

Запуск:
```bash
cd spi_display_scripts
sudo python3 simple_spi_anim.py
# или
sudo python3 pygame_spi_direct.py
```

---

## Быстрые команды для проверки

```bash
# Проверка framebuffer
ls -la /dev/fb*

# Проверка драйвера
dmesg | grep -iE 'mipi|panel|dbi|fb1' | tail -20

# Проверка подсветки
ls -la /sys/class/backlight/

# Включить подсветку
echo 1 | sudo tee /sys/class/backlight/backlight_gpio/brightness

# Перезагрузка драйвера
sudo rmmod panel_mipi_dbi drm_mipi_dbi && sudo modprobe panel_mipi_dbi
```

---

## Примечания

1. **Частота SPI:** 62 MHz - максимальная стабильная для ST7796U. При проблемах уменьшить до 32000000.

2. **Ориентация дисплея:** Изменяется в panel.bin (команда 0x36):
   - `0x48` - портретная (по умолчанию)
   - `0x40` - ландшафтная
   - `0x88` - инвертированная портретная
   - `0xC8` - инвертированная ландшафтная

3. **Производительность:** Ожидаемая частота кадров - 15-25 FPS при выводе полного кадра.

4. **fbcon:** Консоль работает, но может быть медленной при прокрутке больших текстов.

---

## Дата создания инструкции
2026-03-29

## Версия
1.0

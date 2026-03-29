# ST7796U SPI Display - Progress Report

## Цель
Вывод плавного видео (30 FPS) на IPS дисплей ST7796U 320x480 через SPI на Raspberry Pi

## Текущая система
- **OS:** Raspberry Pi OS Bookworm (64-bit)
- **Kernel:** 6.12.47+rpt-rpi-v7
- **Дисплей:** ST7796U IPS 320x480
- **Подключение:**
  - MOSI → GPIO10 (Pin 19)
  - CLK → GPIO11 (Pin 23)
  - CS → GPIO8 (Pin 24)
  - DC → GPIO25 (Pin 22)
  - RST → GPIO24 (Pin 18)
  - BLK → GPIO18 (Pin 12) - PWM подсветка
  - VCC → 3.3V (после стабилизатора)
  - GND → GND

## Что сделано

### 1. SPI включён ✅
```bash
dtparam=spi=on
```
SPI устройства доступны: `/dev/spidev0.0`, `/dev/spidev0.1`

### 2. panel-mipi-dbi модуль ядра ✅
Модуль доступен в ядре:
- `/lib/modules/6.12.47+rpt-rpi-v7/kernel/drivers/gpu/drm/panel-mipi-dbi.ko.xz`
- `/lib/modules/6.12.47+rpt-rpi-v7/kernel/drivers/gpu/drm/drm_mipi_dbi.ko.xz`

### 3. panel.bin создан ✅
Файл инициализации: `/lib/firmware/panel.bin` (89 байт)
Содержит правильную последовательность инициализации ST7796U из TFT_eSPI

### 4. Проблема найдена ✅
**SPI устройство привязано к spidev, а не к panel-mipi-dbi!**

Решение:
```bash
# Blacklist spidev
echo 'blacklist spidev' | sudo tee /etc/modprobe.d/blacklist-spidev.conf

# Unbind spidev
echo -n 'spi0.0' | sudo tee /sys/bus/spi/drivers/spidev/unbind

# Bind panel-mipi-dbi
echo 'panel-mipi-dbi-spi' | sudo tee /sys/bus/spi/devices/spi0.0/driver_override
sudo modprobe panel-mipi-dbi
```

### 5. Custom DT Overlay создан ✅
Файл: `/boot/firmware/overlays/mipi-st7796.dtbo`

Содержит:
- target: /soc/spi@7e204000
- compatible: panel-mipi-dbi-spi
- GPIO: reset=24, dc=25, backlight=18
- resolution: 320x480
- spi-max-frequency: 62000000

## Текущий статус

### Конфигурация (/boot/config.txt):
```
dtoverlay=vc4-kms-v3d
max_framebuffers=1
dtoverlay=mipi-st7796
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt=320 480 60 1 0 0 0
hdmi_drive=2
```

### Последний шаг:
После перезагрузки проверить:
```bash
# 1. Проверить framebuffer
ls -la /dev/fb*

# 2. Проверить загрузку драйвера
dmesg | grep -i 'mipi\|panel\|dbi\|fb1'

# 3. Проверить backlight
ls -la /sys/class/backlight/

# 4. Если /dev/fb1 появился - тестировать вывод
```

## Ожидаемый результат
- `/dev/fb1` - framebuffer для SPI дисплея
- `/sys/class/backlight/` - управление подсветкой
- **15-25 FPS** при выводе полного кадра через DMA

## Для продолжения
```bash
# После перезагрузки
ssh qummy@192.168.0.8

# Проверить что работает
ls -la /dev/fb*
dmesg | tail -30

# Если fb1 есть - тестировать вывод
echo "Тест" > /dev/fb1 2>/dev/null || python3 test_fb.py

# Для видео через framebuffer
sudo apt install -y mplayer
mplayer -vo fbdev2:/dev/fb1 -zoom -x 320 -y 480 video.mp4
```

## Файлы проекта
- `st7796_display.py` - Python тестовый скрипт (работает, ~1 FPS)
- `pygame_st7796_display.py` - Pygame анимация (медленно)
- `ST7796U.pdf` - Datasheet
- `ST7796U_PROGRESS.md` - этот файл

## Дата последнего обновления
2025-03-29 22:27 UTC

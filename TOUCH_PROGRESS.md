# ST7796U CTP - Тачскрин Progress Report

## Оборудование
- **Дисплей:** ST7796U IPS 320x480 (SPI)
- **Тачскрин:** Ёмкостный (CTP) контроллер FT5206/FT5336
- **Плата:** Raspberry Pi Zero 2 W

## Подключение пинов тачскрина

| Дисплей | Raspberry Pi | GPIO | Pin # | Назначение |
|---------|--------------|------|-------|------------|
| ctp_sda | SDA          | 2    | 3     | I2C Data   |
| ctp_scl | SCL          | 3    | 5     | I2C Clock  |
| ctp_rst | GPIO27       | 27   | 13    | Reset (опционально) |

**Важно:** Минимально нужны только SDA и SCL!

---

## Шаг 1: Включение I2C

### 1.1 Добавить в /boot/firmware/config.txt:
```ini
dtparam=i2c_arm=on
```

### 1.2 Перезагрузка:
```bash
sudo reboot
```

### 1.3 Проверка:
```bash
ls /dev/i2c*
# Должно показать: /dev/i2c-1
```

### 1.4 Загрузка модуля (если нужно):
```bash
sudo modprobe i2c-dev
```

---

## Шаг 2: Установка зависимостей

```bash
sudo apt install -y i2c-tools python3-smbus
```

---

## Шаг 3: Поиск тачскрина

```bash
python3 -c "
import smbus
bus = smbus.SMBus(1)
for addr in range(0x03, 0x78):
    try:
        bus.read_byte(addr)
        print(f'Найден девайс: 0x{addr:02X}')
    except:
        pass
"
```

**Ожидаемый результат:** `Найден девайс: 0x38` (FT5206/FT5336)

---

## Шаг 4: Чтение координат

**ВАЖНОЕ ОТКРЫТИЕ:** Тачскрин FT5206/FT5336 выдаёт координаты в **ПРАВИЛЬНОЙ ориентации** без инверсии!

### Неправильно (НЕ делать):
```python
x = WIDTH - raw_x  # НЕ НУЖНО!
y = HEIGHT - raw_y # НЕ НУЖНО!
```

### Правильно:
```python
x = raw_x  # Оставляем как есть
y = raw_y  # Оставляем как есть
```

### Скрипт для проверки touch_coordinates.py:
```python
#!/usr/bin/env python3
import smbus
import time

WIDTH = 320
HEIGHT = 480
TOUCH_ADDR = 0x38

bus = smbus.SMBus(1)

while True:
    touch_count = bus.read_byte_data(TOUCH_ADDR, 0x02)
    if touch_count > 0:
        xh = bus.read_byte_data(TOUCH_ADDR, 0x03)
        xl = bus.read_byte_data(TOUCH_ADDR, 0x04)
        yh = bus.read_byte_data(TOUCH_ADDR, 0x05)
        yl = bus.read_byte_data(TOUCH_ADDR, 0x06)
        
        x = ((xh & 0x0F) << 8) | xl
        y = ((yh & 0x0F) << 8) | yl
        
        # БЕЗ ИНВЕРСИИ!
        print(f"X={x:3d}, Y={y:3d}")
    
    time.sleep(0.05)
```

---

## Шаг 5: Кнопки с тачскрином

Файл: `touch_buttons.py`

**Ключевые моменты:**

1. **Координаты тачскрина НЕ инвертируются**
2. Кнопки рисуются в порядке сверху-вниз:
   - LIGHT: y=50
   - FAN: y=130
   - HEATER: y=210
   - PUMP: y=290

3. Проверка попадания:
```python
if (btn['x'] <= x <= btn['x'] + btn['w'] and 
    btn['y'] <= y <= btn['y'] + btn['h']):
    btn['state'] = not btn['state']
```

---

## Проблема с инверсией (история ошибки)

### Что было сделано неправильно:

1. **Тест с крестиком** (`touch_test_coords.py`):
   - Я рисовал крестик в инвертированных координатах
   - Крестик появлялся в "зеркальном" месте
   - **Вывод был неверный:** "тачскрин зеркалит"

2. **Кнопки не работали:**
   - Касаешься FAN (y=159)
   - Я инвертировал: y = 480 - 159 = 321
   - 321 — это PUMP (нижняя кнопка)
   - **Срабатывала не та кнопка!**

### Правильное решение:
- **НЕ инвертировать координаты**
- Тачскрин FT5206/FT5336 выдаёт координаты в правильной ориентации
- Raw координаты = координаты дисплея

---

## Файлы проекта

| Файл | Назначение |
|------|------------|
| `touch_coordinates.py` | Чтение координат с тачскрина |
| `touch_buttons.py` | Интерактивные кнопки |
| `touch_test_coords.py` | Тест координат с крестиком |
| `touch_reset_scan.py` | Reset и сканирование I2C |

---

## Запуск

```bash
cd ~/spi_scripts

# Проверка координат
sudo python3 touch_coordinates.py

# Кнопки
sudo python3 touch_buttons.py
```

**Для остановки:** Ctrl+C

---

## Итог

✅ **Тачскрин FT5206/FT5336 работает в правильной ориентации**
✅ **Координаты НЕ нужно инвертировать**
✅ **Кнопки срабатывают точно в месте касания**
✅ **I2C адрес: 0x38**
✅ **Достаточно подключить только SDA и SCL**

---

## Дата
2026-03-30

## Версия
1.0 (финальная - координаты без инверсии)

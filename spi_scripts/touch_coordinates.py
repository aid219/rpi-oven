#!/usr/bin/env python3
"""
Чтение координат с тачскрина ST7796U CTP (FT5206/FT5336)
Адрес: 0x38
"""

import smbus
import time

# Адрес тачскрина
TOUCH_ADDR = 0x38

# Регистры FT5206/FT5336
REG_TOUCH = 0x02  # Количество касаний
REG_XH = 0x03     # X старшие биты
REG_XL = 0x04     # X младшие биты
REG_YH = 0x05     # Y старшие биты
REG_YL = 0x06     # Y младшие биты

# Размеры дисплея
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 480

def main():
    print("=== Тачскрин ST7796U CTP ===")
    print("Адрес: 0x38 (FT5206/FT5336)")
    print("Нажми Ctrl+C для выхода\n")
    
    # I2C
    try:
        bus = smbus.SMBus(1)
    except Exception as e:
        print(f"Ошибка I2C: {e}")
        print("Загрузи модуль: sudo modprobe i2c-dev")
        return
    
    last_touch = False
    
    try:
        while True:
            # Проверяем количество касаний
            try:
                touch_count = bus.read_byte_data(TOUCH_ADDR, REG_TOUCH)
            except:
                print("Ошибка чтения I2C - проверь подключение")
                time.sleep(1)
                continue
            
            if touch_count > 0:
                # Есть касание - читаем координаты
                try:
                    xh = bus.read_byte_data(TOUCH_ADDR, REG_XH)
                    xl = bus.read_byte_data(TOUCH_ADDR, REG_XL)
                    yh = bus.read_byte_data(TOUCH_ADDR, REG_YH)
                    yl = bus.read_byte_data(TOUCH_ADDR, REG_YL)
                    
                    # Собираем координаты
                    x = ((xh & 0x0F) << 8) | xl
                    y = ((yh & 0x0F) << 8) | yl
                    
                    # Корректируем для ST7796U (инверсия)
                    x = SCREEN_WIDTH - x
                    y = SCREEN_HEIGHT - y
                    
                    # Ограничиваем
                    x = max(0, min(SCREEN_WIDTH, x))
                    y = max(0, min(SCREEN_HEIGHT, y))
                    
                    if not last_touch:
                        print(f"Касание: X={x:3d}, Y={y:3d}")
                    else:
                        print(f"        X={x:3d}, Y={y:3d}")
                    
                    last_touch = True
                    
                except Exception as e:
                    print(f"Ошибка координат: {e}")
                    last_touch = False
            else:
                if last_touch:
                    print("Отпускание")
                    last_touch = False
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nОстановлено")
    finally:
        bus.close()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Скрипт для чтения координат с тачскрина ST7796U CTP
Поддерживает: FT5206, FT5336, FT5406 (самые частые)
"""

import smbus
import time
import sys

# Адреса контроллеров тачскрина
TOUCH_ADDRESSES = {
    'FT5206': 0x38,  # Самый частый
    'FT5336': 0x38,
    'FT5406': 0x38,
    'GT911': 0x14,
    'CST816': 0x15,
}

# Регистры для FT5206/FT5336
FT_TOUCH_ID = 0x02      # ID касания
FT_XH = 0x03            # X старшие биты
FT_XL = 0x04            # X младшие биты
FT_YH = 0x05            # Y старшие биты
FT_YL = 0x06            # Y младшие биты
FT_TOUCH_EVENT = 0x00   # Событие касания

def detect_touch_controller(bus):
    """Найти контроллер тачскрина"""
    for name, addr in TOUCH_ADDRESSES.items():
        try:
            data = bus.read_byte(addr)
            print(f"Найден тачскрин: {name} по адресу 0x{addr:02X}")
            return name, addr
        except:
            pass
    print("Тачскрин не найден!")
    return None, None

def read_touch_ft(bus, addr):
    """Читать координаты для FT5206/FT5336"""
    try:
        # Проверяем есть ли касание
        touch_count = bus.read_byte_data(addr, FT_TOUCH_ID)
        if touch_count == 0:
            return None
        
        # Читаем координаты первого касания
        xh = bus.read_byte_data(addr, FT_XH)
        xl = bus.read_byte_data(addr, FT_XL)
        yh = bus.read_byte_data(addr, FT_YH)
        yl = bus.read_byte_data(addr, FT_YL)
        
        x = ((xh & 0x0F) << 8) | xl
        y = ((yh & 0x0F) << 8) | yl
        
        # ST7796U имеет ориентацию 320x480
        # Возможно нужно отзеркалить
        x = 320 - x
        y = 480 - y
        
        return (x, y)
    except Exception as e:
        return None

def main():
    print("=== Тачскрин ST7796U CTP ===")
    print("Нажми Ctrl+C для выхода\n")
    
    # Открываем I2C шину
    try:
        bus = smbus.SMBus(1)
    except Exception as e:
        print(f"Ошибка открытия I2C: {e}")
        print("Убедись что I2C включён (dtparam=i2c_arm=on в /boot/firmware/config.txt)")
        return
    
    # Находим контроллер
    controller, addr = detect_touch_controller(bus)
    if controller is None:
        bus.close()
        return
    
    print(f"Адрес I2C: 0x{addr:02X}")
    print("\nКоординаты касания:")
    print("-" * 30)
    
    last_coords = None
    
    try:
        while True:
            if controller in ['FT5206', 'FT5336', 'FT5406']:
                coords = read_touch_ft(bus, addr)
            else:
                coords = None
            
            if coords:
                if coords != last_coords:
                    print(f"X: {coords[0]:3d}, Y: {coords[1]:3d}")
                    last_coords = coords
            else:
                if last_coords:
                    print("Касание прекращено")
                    last_coords = None
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nОстановлено")
    finally:
        bus.close()

if __name__ == "__main__":
    main()

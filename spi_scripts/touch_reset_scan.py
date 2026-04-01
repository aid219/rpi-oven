#!/usr/bin/env python3
"""
Скрипт для поиска тачскрина ST7796U CTP с reset
"""

import smbus
import time
import RPi.GPIO as GPIO

# Пины
RST_PIN = 27  # ctp_rst

# Адреса контроллеров
TOUCH_ADDRESSES = [0x38, 0x14, 0x15, 0x2A, 0x4A]  # FT5206, GT911, CST816 и др.

def reset_touch():
    """Сделать reset тачскрина"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RST_PIN, GPIO.OUT)
    
    print("Делаю reset тачскрина...")
    GPIO.output(RST_PIN, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.1)
    print("Reset выполнен")

def scan_i2c(bus):
    """Сканировать I2C шину"""
    print("\nСканирование I2C...")
    found = []
    for addr in range(0x03, 0x78):
        try:
            bus.read_byte(addr)
            found.append(addr)
            print(f"  0x{addr:02X} - найден")
        except:
            pass
    return found

def try_read_touch(bus, addr):
    """Попробовать прочитать из тачскрина"""
    try:
        # Пробуем разные регистры
        for reg in [0x00, 0x02, 0x80, 0x81]:
            try:
                data = bus.read_byte_data(addr, reg)
                print(f"  0x{addr:02X}[0x{reg:02X}] = 0x{data:02X}")
                return True
            except:
                pass
        return False
    except:
        return False

def main():
    print("=== Тачскрин ST7796U CTP ===\n")
    
    # Reset
    reset_touch()
    
    # I2C
    try:
        bus = smbus.SMBus(1)
        print("I2C шина открыта\n")
    except Exception as e:
        print(f"Ошибка I2C: {e}")
        return
    
    # Сканируем
    found = scan_i2c(bus)
    
    if found:
        print("\nПопытка чтения из тачскрина...")
        for addr in found:
            if try_read_touch(bus, addr):
                print(f"✓ Тачскрин найден по адресу 0x{addr:02X}")
                break
        else:
            print("Тачскрин не найден среди устройств")
    else:
        print("\nНичего не найдено на I2C!")
        print("Проверь:")
        print("  - ctp_sda → GPIO2 (Pin 3)")
        print("  - ctp_scl → GPIO3 (Pin 5)")
        print("  - ctp_rst → GPIO27 (Pin 13)")
    
    bus.close()
    GPIO.cleanup()
    print("\nГотово")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Создать panel.bin в формате panel-mipi-dbi для ST7796U
С ИНВЕРСИЕЙ цветов (нормальный режим)
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

# Interface Mode Control - Memory Data Access Control
# 0x88 = MY=1, MX=0, MV=0, RGB=1 (инвертированная ориентация)
commands += cmd(0x36, [0x88])

# Pixel Format
commands += cmd(0x3A, [0x55])  # 16-bit/pixel

# Frame Rate Control
commands += cmd(0xB4, [0x01])

# Display Inversion Control - 0x20 = Display Inversion OFF
commands += cmd(0x20)

# Display Inversion Mode - 0xB4 bit 2 = 0 для dot inversion
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

with open('panel_fixed.bin', 'wb') as f:
    f.write(firmware)

print(f"Создан panel_fixed.bin: {len(firmware)} байт")
print("Добавлена команда 0x21 (Display Inversion ON)")

#!/usr/bin/env python3
"""
Создать panel.bin в формате panel-mipi-dbi для ST7796U
БЕЗ инверсии - нормальные цвета
"""

MAGIC = b'MIPI DBI' + b'\x00' * 7
VERSION = b'\x01'

def cmd(code, data=None):
    if data is None:
        data = []
    return bytes([code, len(data)]) + bytes(data)

def delay(ms):
    return bytes([0x00, 0x01, ms & 0xFF])

commands = bytearray()

# Reset
commands += cmd(0x01)
commands += delay(120)

# Sleep Out
commands += cmd(0x11)
commands += delay(150)

# Command 2 (Protection)
commands += cmd(0xF0, [0xC3])
commands += cmd(0xF0, [0x96])

# Memory Data Access Control - нормальная ориентация
commands += cmd(0x36, [0x48])

# Pixel Format - 16-bit/pixel RGB565
commands += cmd(0x3A, [0x55])

# Frame Rate Control
commands += cmd(0xB4, [0x01])

# Display Inversion OFF - нормальные цвета
commands += cmd(0x20)

# Display Control
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
commands += cmd(0x2A, [0x00, 0x00, 0x01, 0x3F])

# Row Address Set
commands += cmd(0x2B, [0x00, 0x00, 0x01, 0xDF])

firmware = MAGIC + VERSION + commands

with open('panel_normal.bin', 'wb') as f:
    f.write(firmware)

print(f"Создан panel_normal.bin: {len(firmware)} байт")

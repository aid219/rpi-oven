#!/usr/bin/env python3
"""
Кнопки с отладкой координат
"""

import smbus
import time
import struct
import fcntl
import mmap

WIDTH = 320
HEIGHT = 480
TOUCH_ADDR = 0x38

def rgb565(r, g, b):
    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return bytes([color & 0xFF, (color >> 8) & 0xFF])

def draw_filled_rect(fb_mem, line_length, x, y, w, h, color):
    color_bytes = rgb565(*color)
    line = color_bytes * w
    for iy in range(y, y + h):
        fb_mem.seek(iy * line_length + x * 2)
        fb_mem.write(line)

def draw_hline(fb_mem, line_length, x, y, w, color):
    color_bytes = rgb565(*color)
    line = color_bytes * w
    fb_mem.seek(y * line_length + x * 2)
    fb_mem.write(line)

def draw_vline(fb_mem, line_length, x, y, h, color):
    color_bytes = rgb565(*color)
    for iy in range(y, y + h):
        fb_mem.seek(iy * line_length + x * 2)
        fb_mem.write(color_bytes)

def draw_text(fb_mem, line_length, text, x, y, color):
    font = {
        '0': [(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(4,2),(0,3),(4,3),(0,4),(4,4),(1,5),(2,5),(3,5)],
        '1': [(2,0),(1,1),(2,1),(0,2),(1,2),(2,2),(2,3),(2,4),(0,5),(1,5),(2,5),(3,5),(4,5)],
        '2': [(1,0),(2,0),(3,0),(4,0),(0,1),(4,1),(3,2),(2,3),(1,4),(0,5),(1,5),(2,5),(3,5),(4,5)],
        '3': [(1,0),(2,0),(3,0),(4,0),(0,1),(4,1),(2,2),(3,2),(4,2),(4,3),(4,4),(0,5),(1,5),(2,5),(3,5),(4,5)],
        '4': [(0,0),(4,0),(0,1),(4,1),(0,2),(4,2),(0,3),(1,3),(2,3),(3,3),(4,3),(4,4),(4,5)],
        '5': [(0,0),(1,0),(2,0),(3,0),(4,0),(0,1),(0,2),(1,2),(2,2),(3,2),(4,3),(4,4),(0,5),(1,5),(2,5),(3,5),(4,5)],
        '6': [(1,0),(2,0),(3,0),(4,0),(0,1),(0,2),(0,3),(1,3),(2,3),(3,3),(4,3),(0,4),(4,4),(0,5),(1,5),(2,5),(3,5)],
        '7': [(0,0),(1,0),(2,0),(3,0),(4,0),(4,1),(3,2),(2,3),(2,4),(1,5)],
        '8': [(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(4,2),(1,3),(2,3),(3,3),(0,4),(4,4),(1,5),(2,5),(3,5)],
        '9': [(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(1,2),(2,2),(3,2),(4,2),(4,3),(4,4),(0,5),(1,5),(2,5),(3,5)],
        ' ': [],
        'X': [(0,0),(4,0),(1,1),(3,1),(2,2),(1,3),(3,3),(0,4),(4,4),(0,5),(4,5)],
        'Y': [(0,0),(4,0),(1,1),(3,1),(2,2),(2,3),(2,4),(2,5)],
        'T': [(0,0),(1,0),(2,0),(3,0),(4,0),(2,1),(2,2),(2,3),(2,4),(2,5)],
        'c': [(2,2),(3,2),(4,2),(0,3),(0,4),(1,4),(2,4),(3,4)],
        'h': [(0,0),(0,1),(0,2),(0,3),(0,4),(1,2),(2,2),(1,3),(2,3),(1,4),(2,4)],
        'o': [(1,2),(2,2),(3,2),(0,3),(4,3),(0,4),(4,4),(1,5),(2,5),(3,5)],
        'r': [(0,2),(1,2),(2,2),(0,3),(0,4),(0,5)],
        'd': [(3,0),(3,1),(3,2),(3,3),(3,4),(3,5),(1,2),(2,2),(4,2),(0,3),(4,3),(0,4),(4,4),(1,5),(2,5),(3,5)],
        'i': [(2,0),(2,2),(2,3),(2,4),(0,5),(1,5),(2,5),(3,5),(4,5)],
        's': [(2,2),(3,2),(4,2),(0,3),(0,4),(1,4),(2,4),(3,4),(0,5),(1,5),(2,5)],
        'L': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(1,5),(2,5),(3,5),(4,5)],
        'I': [(2,0),(2,1),(2,2),(2,3),(2,4),(0,5),(1,5),(2,5),(3,5),(4,5)],
        'G': [(2,0),(3,0),(4,0),(0,1),(0,2),(0,3),(0,4),(1,4),(2,4),(3,4),(4,4),(1,5),(2,5),(3,5),(4,5)],
        'H': [(0,0),(4,0),(0,1),(4,1),(0,2),(4,2),(0,3),(1,3),(2,3),(3,3),(4,3),(0,4),(4,4),(0,5),(4,5)],
        'N': [(0,0),(4,0),(0,1),(1,1),(3,1),(4,1),(0,2),(2,2),(4,2),(0,3),(4,3),(0,4),(4,4),(0,5),(4,5)],
        'F': [(0,0),(1,0),(2,0),(3,0),(4,0),(0,1),(0,2),(0,3),(0,4),(0,5),(1,5),(2,5),(3,5)],
        'A': [(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(4,2),(0,3),(1,3),(2,3),(3,3),(4,3),(0,4),(4,4),(0,5),(4,5)],
        'E': [(0,0),(1,0),(2,0),(3,0),(4,0),(0,1),(0,2),(0,3),(0,4),(0,5),(1,5),(2,5),(3,5),(4,5)],
        'R': [(0,0),(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(4,2),(0,3),(4,3),(0,4),(2,4),(0,5),(4,5)],
        'P': [(0,0),(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(4,2),(0,3),(4,3),(0,4),(0,5),(1,5),(2,5),(3,5)],
        'U': [(0,0),(4,0),(0,1),(4,1),(0,2),(4,2),(0,3),(4,3),(0,4),(4,4),(1,5),(2,5),(3,5)],
        'M': [(0,0),(4,0),(0,1),(1,1),(3,1),(4,1),(0,2),(2,2),(4,2),(0,3),(4,3),(0,4),(4,4),(0,5),(4,5)],
        'O': [(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(4,2),(0,3),(4,3),(0,4),(4,4),(1,5),(2,5),(3,5)],
    }
    
    for ci, char in enumerate(text.upper()):
        if char in font:
            for px, py in font[char]:
                dx = x + ci * 6 + px
                dy = y + py
                if 0 <= dx < WIDTH and 0 <= dy < HEIGHT:
                    fb_mem.seek(dy * line_length + dx * 2)
                    fb_mem.write(rgb565(*color))

def draw_button(fb_mem, line_length, btn, label, state):
    x, y, w, h = btn['x'], btn['y'], btn['w'], btn['h']
    color = btn['color_on'] if state else btn['color_off']
    
    draw_filled_rect(fb_mem, line_length, x, y, w, h, color)
    draw_hline(fb_mem, line_length, x, y, w, (255, 255, 255))
    draw_hline(fb_mem, line_length, x, y + h - 1, w, (255, 255, 255))
    draw_vline(fb_mem, line_length, x, y, h, (255, 255, 255))
    draw_vline(fb_mem, line_length, x + w - 1, y, h, (255, 255, 255))
    
    # Текст
    text_w = len(label) * 6
    text_x = x + (w - text_w) // 2
    draw_text(fb_mem, line_length, label, text_x, y + h//2 - 3, (255, 255, 255))
    
    # Индикатор
    ind_color = (0, 255, 0) if state else (80, 80, 80)
    draw_filled_rect(fb_mem, line_length, x + w - 25, y + 8, 15, 15, ind_color)

def get_touch(bus):
    try:
        touch_count = bus.read_byte_data(TOUCH_ADDR, 0x02)
        if touch_count > 0:
            xh = bus.read_byte_data(TOUCH_ADDR, 0x03)
            xl = bus.read_byte_data(TOUCH_ADDR, 0x04)
            yh = bus.read_byte_data(TOUCH_ADDR, 0x05)
            yl = bus.read_byte_data(TOUCH_ADDR, 0x06)
            
            raw_x = ((xh & 0x0F) << 8) | xl
            raw_y = ((yh & 0x0F) << 8) | yl
            
            # БЕЗ инверсии - тачскрин в правильной ориентации
            x = raw_x
            y = raw_y
            
            return (max(0, min(WIDTH-1, x)), max(0, min(HEIGHT-1, y)), raw_x, raw_y)
    except:
        pass
    return None

def main():
    # Кнопки в нормальном порядке (LIGHT сверху, PUMP снизу)
    buttons = [
        {'x': 40, 'y': 50, 'w': 240, 'h': 60, 'color_off': (50, 50, 50), 'color_on': (255, 180, 0), 'state': False},  # LIGHT
        {'x': 40, 'y': 130, 'w': 240, 'h': 60, 'color_off': (50, 50, 50), 'color_on': (0, 180, 255), 'state': False},  # FAN
        {'x': 40, 'y': 210, 'w': 240, 'h': 60, 'color_off': (50, 50, 50), 'color_on': (255, 50, 50), 'state': False},  # HEATER
        {'x': 40, 'y': 290, 'w': 240, 'h': 60, 'color_off': (50, 50, 50), 'color_on': (50, 255, 50), 'state': False},   # PUMP
    ]
    labels = ['LIGHT', 'FAN', 'HEATER', 'PUMP']
    
    fb = open('/dev/fb0', 'r+b')
    fix_info = fcntl.ioctl(fb, 0x4602, bytes(128))
    line_length = struct.unpack('I', fix_info[16:20])[0]
    if line_length == 0:
        line_length = WIDTH * 2
    
    fb_mem = mmap.mmap(fb.fileno(), line_length * HEIGHT, prot=mmap.PROT_WRITE)
    bus = smbus.SMBus(1)
    
    # Рисуем кнопки
    for i, btn in enumerate(buttons):
        draw_button(fb_mem, line_length, btn, labels[i], btn['state'])
    
    # Зона отладки (низ экрана)
    draw_filled_rect(fb_mem, line_length, 0, 400, WIDTH, 80, (30, 30, 30))
    draw_text(fb_mem, line_length, "Touch coords:", 10, 410, (200, 200, 200))
    
    was_touching = False
    last_touch_time = 0
    
    try:
        while True:
            touch = get_touch(bus)
            
            if touch and not was_touching:
                current_time = time.time()
                if current_time - last_touch_time > 0.3:
                    x, y, raw_x, raw_y = touch
                    
                    # Показываем координаты
                    draw_filled_rect(fb_mem, line_length, 0, 400, WIDTH, 80, (30, 30, 30))
                    draw_text(fb_mem, line_length, f"Raw:{raw_x},{raw_y}", 10, 410, (255, 255, 0))
                    draw_text(fb_mem, line_length, f"Adj:{x},{y}", 10, 425, (0, 255, 255))
                    
                    # Крестик в точке касания
                    draw_hline(fb_mem, line_length, max(0,x-10), y, 20, (255, 0, 0))
                    draw_vline(fb_mem, line_length, x, max(0,y-10), 20, (255, 0, 0))
                    
                    for i, btn in enumerate(buttons):
                        if (btn['x'] <= x <= btn['x'] + btn['w'] and 
                            btn['y'] <= y <= btn['y'] + btn['h']):
                            btn['state'] = not btn['state']
                            draw_button(fb_mem, line_length, btn, labels[i], btn['state'])
                            draw_text(fb_mem, line_length, f"Btn:{labels[i]}", 150, 410, (0, 255, 0))
                            last_touch_time = current_time
                            break
                
                was_touching = True
            elif not touch:
                was_touching = False
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        pass
    finally:
        fb_mem.close()
        fb.close()
        bus.close()

if __name__ == "__main__":
    main()

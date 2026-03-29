#!/usr/bin/env python3
"""
Pygame на SPI дисплее ST7796U через прямой доступ к framebuffer
Используем mmap для записи напрямую в /dev/fb1
"""

import os
import sys
import struct
import fcntl
import mmap
import time
import math

# Параметры дисплея
WIDTH = 320
HEIGHT = 480
BYTES_PER_PIXEL = 2  # RGB565

def rgb565(r, g, b):
    """Конвертировать RGB888 в RGB565 (big-endian)"""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def rgb565_le(r, g, b):
    """Конвертировать RGB888 в RGB565 (little-endian)"""
    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return bytes([color & 0xFF, (color >> 8) & 0xFF])

class FramebufferDisplay:
    """Класс для работы с framebuffer"""
    
    def __init__(self, fb_path='/dev/fb1', width=320, height=480):
        self.width = width
        self.height = height
        self.fb_path = fb_path
        
        # Открываем framebuffer
        self.fb = open(fb_path, 'r+b')
        
        # Получаем информацию о framebuffer
        fix_info = fcntl.ioctl(self.fb, 0x4602, bytes(128))  # FBIOGET_FSCREENINFO
        self.line_length = struct.unpack('I', fix_info[16:20])[0]
        
        if self.line_length == 0:
            self.line_length = width * BYTES_PER_PIXEL
        
        self.fb_size = self.line_length * height
        print(f"Framebuffer: {self.line_length} bytes/line, {self.fb_size} bytes total")
        
        # Отображаем память
        self.fb_mem = mmap.mmap(self.fb.fileno(), self.fb_size, prot=mmap.PROT_WRITE)
        
        # Буфер экрана (для double buffering)
        self.screen_buffer = bytearray(self.line_length * height)
    
    def clear(self, r=0, g=0, b=0):
        """Очистить экран цветом"""
        color = rgb565(r, g, b)
        # Создаём строку цвета
        line = struct.pack('<H', color) * self.width
        # Заполняем буфер
        for y in range(self.height):
            offset = y * self.line_length
            self.screen_buffer[offset:offset + self.width * 2] = line
        self.flip()
    
    def draw_pixel(self, x, y, r, g, b):
        """Нарисовать пиксель в буфере"""
        if 0 <= x < self.width and 0 <= y < self.height:
            color = struct.pack('<H', rgb565(r, g, b))
            offset = y * self.line_length + x * 2
            self.screen_buffer[offset:offset + 2] = color
    
    def draw_line(self, x1, y1, x2, y2, r, g, b):
        """Нарисовать линию (алгоритм Брезенхема)"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            self.draw_pixel(x1, y1, r, g, b)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
    
    def draw_circle(self, cx, cy, radius, r, g, b, fill=False):
        """Нарисовать круг"""
        if fill:
            for y in range(cy - radius, cy + radius + 1):
                for x in range(cx - radius, cx + radius + 1):
                    if (x - cx)**2 + (y - cy)**2 <= radius**2:
                        self.draw_pixel(x, y, r, g, b)
        else:
            # Алгоритм Брезенхема для круга
            x = radius
            y = 0
            err = 0
            
            while x >= y:
                self.draw_pixel(cx + x, cy + y, r, g, b)
                self.draw_pixel(cx + y, cy + x, r, g, b)
                self.draw_pixel(cx - y, cy + x, r, g, b)
                self.draw_pixel(cx - x, cy + y, r, g, b)
                self.draw_pixel(cx - x, cy - y, r, g, b)
                self.draw_pixel(cx - y, cy - x, r, g, b)
                self.draw_pixel(cx + y, cy - x, r, g, b)
                self.draw_pixel(cx + x, cy - y, r, g, b)
                y += 1
                err += 1 + 2 * y
                if 2 * (err - x) + 1 > 0:
                    x -= 1
                    err += 1 - 2 * x
    
    def draw_rect(self, x, y, w, h, r, g, b, fill=False):
        """Нарисовать прямоугольник"""
        if fill:
            for iy in range(y, y + h):
                for ix in range(x, x + w):
                    self.draw_pixel(ix, iy, r, g, b)
        else:
            self.draw_line(x, y, x + w, y, r, g, b)
            self.draw_line(x + w, y, x + w, y + h, r, g, b)
            self.draw_line(x + w, y + h, x, y + h, r, g, b)
            self.draw_line(x, y + h, x, y, r, g, b)
    
    def draw_text_simple(self, text, x, y, r, g, b, scale=2):
        """Простой текст (символы 5x7)"""
        # Простая имитация текста - рамки символов
        font_5x7 = {
            'S': [(1,0),(2,0),(3,0),(4,0),(0,1),(0,2),(1,2),(2,2),(3,2),(4,3),(4,4),(0,5),(1,5),(2,5),(3,5),(4,5)],
            'T': [(0,0),(1,0),(2,0),(3,0),(4,0),(2,1),(2,2),(2,3),(2,4),(2,5)],
            '7': [(0,0),(1,0),(2,0),(3,0),(4,0),(3,1),(2,2),(2,3),(1,4),(1,5)],
            '6': [(1,0),(2,0),(3,0),(4,0),(0,1),(0,2),(0,3),(1,3),(2,3),(3,3),(4,3),(0,4),(4,4),(0,5),(1,5),(2,5),(3,5)],
            '9': [(1,0),(2,0),(3,0),(4,0),(0,1),(4,1),(0,2),(4,2),(1,3),(2,3),(3,3),(4,3),(4,4),(0,5),(1,5),(2,5),(3,5)],
            'U': [(0,0),(4,0),(0,1),(4,1),(0,2),(4,2),(0,3),(4,3),(0,4),(4,4),(1,5),(2,5),(3,5)],
            ' ': []
        }
        
        for ci, char in enumerate(text.upper()):
            if char in font_5x7:
                for px, py in font_5x7[char]:
                    for sy in range(scale):
                        for sx in range(scale):
                            self.draw_pixel(x + ci * 6 * scale + px * scale + sx, 
                                          y + py * scale + sy, r, g, b)
    
    def flip(self):
        """Обновить экран"""
        self.fb_mem.seek(0)
        self.fb_mem.write(self.screen_buffer)
    
    def close(self):
        """Закрыть framebuffer"""
        self.fb_mem.close()
        self.fb.close()


def main():
    """Основная демонстрация"""
    print("=" * 50)
    print("Pygame-стиль демо на SPI дисплее (прямой доступ)")
    print("=" * 50)
    
    display = FramebufferDisplay('/dev/fb1', WIDTH, HEIGHT)
    
    # Цвета
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    ORANGE = (255, 128, 0)
    
    try:
        # 1. Тест цветов
        print("\n1. Тест цветов...")
        for color, name in [(RED, 'RED'), (GREEN, 'GREEN'), (BLUE, 'BLUE'), 
                           (WHITE, 'WHITE'), (BLACK, 'BLACK')]:
            display.clear(*color)
            print(f"  {name}")
            time.sleep(1)
        
        # 2. Градиент
        print("2. Градиент...")
        for y in range(HEIGHT):
            r = int(255 * y / HEIGHT)
            b = int(255 * (HEIGHT - y) / HEIGHT)
            color = struct.pack('<H', rgb565(r, 0, b))
            line = color * WIDTH
            offset = y * display.line_length
            display.screen_buffer[offset:offset + WIDTH * 2] = line
        display.flip()
        time.sleep(2)
        
        # 3. Анимация
        print("3. Анимация (30 сек)...")
        
        # Параметры
        ball_x = WIDTH // 2
        ball_y = HEIGHT // 3
        ball_radius = 20
        ball_vx = 4
        ball_vy = 5
        
        paddle_x = WIDTH // 2
        paddle_y = HEIGHT - 50
        paddle_w = 70
        paddle_h = 12
        
        sun_angle = 0
        
        start_time = time.time()
        frame_count = 0
        fps = 0
        
        while time.time() - start_time < 30:
            # Очистка (градиентный фон)
            for y in range(HEIGHT):
                color_val = int(30 * y / HEIGHT)
                color = struct.pack('<H', rgb565(color_val, color_val, color_val + 30))
                line = color * WIDTH
                offset = y * display.line_length
                display.screen_buffer[offset:offset + WIDTH * 2] = line
            
            # Солнце (вращающееся)
            sun_angle += 3
            cx, cy = WIDTH // 2, 90
            for i in range(12):
                angle = math.radians(sun_angle + i * 30)
                sx1 = cx + int(math.cos(angle) * 30)
                sy1 = cy + int(math.sin(angle) * 30)
                sx2 = cx + int(math.cos(angle) * 50)
                sy2 = cy + int(math.sin(angle) * 50)
                display.draw_line(sx1, sy1, sx2, sy2, *YELLOW)
            
            display.draw_circle(cx, cy, 28, *YELLOW, fill=True)
            display.draw_circle(cx, cy, 28, *WHITE)
            
            # Мяч
            ball_x += ball_vx
            ball_y += ball_vy
            
            # Отскок от стен
            if ball_x - ball_radius <= 0 or ball_x + ball_radius >= WIDTH:
                ball_vx = -ball_vx
            if ball_y - ball_radius <= 70:
                ball_vy = -ball_vy
            
            # Отскок от ракетки
            if (ball_y + ball_radius >= paddle_y and 
                ball_y - ball_radius <= paddle_y + paddle_h and
                ball_x >= paddle_x - paddle_w // 2 and 
                ball_x <= paddle_x + paddle_w // 2):
                ball_vy = -ball_vy
            
            # Ограничение мяча по Y снизу
            if ball_y - ball_radius >= HEIGHT:
                ball_y = HEIGHT // 3
                ball_vy = 5
            
            display.draw_circle(int(ball_x), int(ball_y), ball_radius, *RED, fill=True)
            display.draw_circle(int(ball_x), int(ball_y), ball_radius, *WHITE)
            
            # Ракетка (движется за мячом)
            target_x = ball_x
            if target_x < paddle_w // 2:
                target_x = paddle_w // 2
            if target_x > WIDTH - paddle_w // 2:
                target_x = WIDTH - paddle_w // 2
            paddle_x += (target_x - paddle_x) * 0.1
            
            display.draw_rect(int(paddle_x - paddle_w // 2), paddle_y, 
                            paddle_w, paddle_h, *GREEN, fill=True)
            display.draw_rect(int(paddle_x - paddle_w // 2), paddle_y, 
                            paddle_w, paddle_h, *WHITE)
            
            # FPS
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed >= 1.0:
                fps = int(frame_count / elapsed)
                frame_count = 0
                start_time = time.time()
            
            # Индикатор FPS
            display.draw_text_simple(f"FPS:{fps}", 5, 5, *CYAN, scale=2)
            
            display.flip()
            time.sleep(1/60)  # ~60 FPS
        
        # 4. Финальный экран
        print("4. Финальный экран...")
        display.clear(20, 20, 50)
        
        # Рамка
        display.draw_rect(10, 10, WIDTH - 20, HEIGHT - 20, *WHITE)
        
        # Текст (символами)
        display.draw_text_simple("ST7796U", WIDTH // 2 - 42, 100, *YELLOW, scale=3)
        display.draw_text_simple("320x480", WIDTH // 2 - 36, 160, *WHITE, scale=2)
        display.draw_text_simple("SPI DISPLAY", WIDTH // 2 - 54, 200, *CYAN, scale=2)
        
        # Цветные полосы
        colors = [RED, GREEN, BLUE, CYAN, MAGENTA, ORANGE]
        for i, color in enumerate(colors):
            display.draw_rect(20, 260 + i * 25, WIDTH - 40, 20, *color, fill=True)
        
        display.flip()
        
        print("\nГотово! Финальный экран на дисплее.")
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\nПрервано пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        display.close()
        print("Завершено!")

if __name__ == "__main__":
    main()

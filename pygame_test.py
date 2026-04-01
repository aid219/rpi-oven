#!/usr/bin/env python3
"""
Pygame тест для Raspberry Pi с FT6336U тачскрином
Вывод во фреймбуфер, 30 FPS анимация
"""

import os
import time
import math
import pygame

# Настройки
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 480
TARGET_FPS = 30
FB_DEVICE = '/dev/fb0'

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)


class BouncingBall:
    """Анимированный прыгающий мяч"""
    
    def __init__(self, x, y, radius, color, speed_x, speed_y):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
    
    def update(self, width, height):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Отскок от стен
        if self.x - self.radius < 0 or self.x + self.radius > width:
            self.speed_x = -self.speed_x
            self.x = max(self.radius, min(self.x, width - self.radius))
        
        if self.y - self.radius < 0 or self.y + self.radius > height:
            self.speed_y = -self.speed_y
            self.y = max(self.radius, min(self.y, height - self.radius))
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


class TouchPoint:
    """Точка касания тачскрина"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alpha = 255
        self.radius = 30
    
    def update(self):
        self.alpha -= 5
        self.radius += 1
        return self.alpha > 0
    
    def draw(self, surface):
        if self.alpha > 0:
            color = (255, 255, 255, self.alpha)
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color[:3], min(100, self.alpha)), 
                             (self.radius, self.radius), self.radius)
            surface.blit(s, (self.x - self.radius, self.y - self.radius))


class TouchScreen:
    """Обработчик тачскрина"""
    
    def __init__(self):
        self.touch_device = None
        self.points = []
        self.init_touch()
    
    def init_touch(self):
        """Инициализация тачскрина"""
        try:
            devices = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            for device in devices:
                device.init()
                print(f"Joystick: {device.get_name()}")
            
            # Пробуем найти тачскрин через evdev
            import evdev
            for path in evdev.list_devices():
                try:
                    device = evdev.InputDevice(path)
                    if "1-0038" in device.name or "EP0110" in device.name or "ft" in device.name.lower():
                        print(f"Found touchscreen: {device.name} at {path}")
                        self.touch_device = device
                        break
                except:
                    pass
        except Exception as e:
            print(f"Touch init error: {e}")
    
    def update(self):
        """Обновление тачскрина"""
        if not self.touch_device:
            return []
        
        try:
            new_points = []
            for event in self.touch_device.read_loop():
                if event.type == evdev.ecodes.EV_ABS:
                    if event.code == evdev.ecodes.ABS_MT_POSITION_X:
                        x = event.value
                    elif event.code == evdev.ecodes.ABS_MT_POSITION_Y:
                        y = event.value
                    elif event.code == evdev.ecodes.ABS_X:
                        x = event.value
                    elif event.code == evdev.ecodes.ABS_Y:
                        y = event.value
                elif event.type == evdev.ecodes.EV_KEY and event.value == 1:
                    new_points.append(TouchPoint(x, y))
            
            self.points.extend(new_points)
            
            # Обновляем и удаляем старые точки
            self.points = [p for p in self.points if p.update()]
            
            return self.points
        except:
            return []
    
    def get_touches(self):
        """Получить текущие касания"""
        return [(p.x, p.y) for p in self.points if p.alpha > 100]


def main():
    """Основная функция"""
    
    # Устанавливаем фреймбуфер
    os.environ['SDL_FBDEV'] = FB_DEVICE
    os.environ['SDL_VIDEODRIVER'] = 'framebuffer'
    
    # Инициализация pygame
    pygame.init()
    pygame.display.init()
    
    # Создаём окно
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("FT6336U Touch Test")
    
    # Часы для FPS
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    
    # Создаём объекты
    balls = [
        BouncingBall(50, 50, 20, RED, 3, 2),
        BouncingBall(150, 100, 25, GREEN, -2, 3),
        BouncingBall(250, 150, 15, BLUE, 4, -2),
        BouncingBall(100, 200, 18, CYAN, -3, -3),
        BouncingBall(200, 250, 22, MAGENTA, 2, -4),
    ]
    
    touch_handler = TouchScreen()
    
    # Переменные для FPS
    running = True
    frame_count = 0
    start_time = time.time()
    fps_values = []
    
    # Угол для вращения цветов
    color_angle = 0
    
    print("Starting pygame loop...")
    print(f"Screen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"Target FPS: {TARGET_FPS}")
    
    try:
        while running:
            # Обработка событий pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_q:
                        running = False
            
            # Обновление тачскрина
            touch_handler.update()
            touches = touch_handler.get_touches()
            
            # Обновление мячей
            for ball in balls:
                ball.update(SCREEN_WIDTH, SCREEN_HEIGHT)
            
            # Очистка экрана
            screen.fill(BLACK)
            
            # Рисуем сетку
            for x in range(0, SCREEN_WIDTH, 40):
                pygame.draw.line(screen, (30, 30, 30), (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, 40):
                pygame.draw.line(screen, (30, 30, 30), (0, y), (SCREEN_WIDTH, y))
            
            # Рисуем мячи
            for ball in balls:
                ball.draw(screen)
            
            # Рисуем точки касания
            for point in touch_handler.points:
                point.draw(screen)
            
            # Рисуем информацию
            color_angle += 0.05
            r = int(127 + 127 * math.sin(color_angle))
            g = int(127 + 127 * math.sin(color_angle + 2))
            b = int(127 + 127 * math.sin(color_angle + 4))
            
            info_text = f"FPS: {int(clock.get_fps())} | Touches: {len(touches)}"
            text_surface = font.render(info_text, True, (r, g, b))
            screen.blit(text_surface, (10, 10))
            
            # Рисуем координаты касаний
            for i, (tx, ty) in enumerate(touches):
                coord_text = f"T{i}: ({tx}, {ty})"
                coord_surface = small_font.render(coord_text, True, YELLOW)
                screen.blit(coord_surface, (10, 40 + i * 20))
            
            # Обновляем экран
            pygame.display.flip()
            
            # Держим 30 FPS
            clock.tick(TARGET_FPS)
            
            # Статистика
            frame_count += 1
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                if elapsed > 0:
                    current_fps = frame_count / elapsed
                    fps_values.append(current_fps)
                    if len(fps_values) > 10:
                        fps_values.pop(0)
                    avg_fps = sum(fps_values) / len(fps_values)
                    print(f"FPS: {current_fps:.1f} (avg: {avg_fps:.1f})")
                start_time = time.time()
                frame_count = 0
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        print("Pygame stopped")


if __name__ == '__main__':
    main()

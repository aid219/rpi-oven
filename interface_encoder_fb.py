#!/usr/bin/env python3
"""UI для энкодера — только framebuffer, без pygame display"""
import pygame
import json
import os
import struct
import numpy as np

class UI:
    def __init__(self, config_path):
        pygame.init()
        pygame.font.init()
        
        # Размеры экрана
        self.width = 1024
        self.height = 600
        
        # Читаем из sysfs
        try:
            with open('/sys/class/graphics/fb0/virtual_size') as f:
                size = f.read().strip()
                self.width, self.height = map(int, size.split(','))
        except:
            pass
        
        try:
            with open('/sys/class/graphics/fb0/stride') as f:
                self.stride = int(f.read().strip())
        except:
            self.stride = self.width * 2  # RGB565
        
        # Открываем framebuffer
        self.fb = open('/dev/fb0', 'r+b')
        
        # Создаём поверхность для рендеринга
        self.screen = pygame.Surface((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.big_font = pygame.font.Font(None, 120)
        self.font = pygame.font.Font(None, 36)
        
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.value = self.config.get('value', 0)
        self.box_x = self.config.get('box_x', 362)
        self.box_y = self.config.get('box_y', 250)
        self.box_width = self.config.get('box_width', 300)
        self.box_height = self.config.get('box_height', 150)
    
    def set_value(self, value):
        self.value = value
    
    def draw(self):
        # Фон
        self.screen.fill((30, 30, 50))
        
        # Рамка окошка
        pygame.draw.rect(self.screen, (100, 100, 120), 
                        (self.box_x, self.box_y, self.box_width, self.box_height), 
                        border_radius=20)
        pygame.draw.rect(self.screen, (200, 200, 220), 
                        (self.box_x, self.box_y, self.box_width, self.box_height), 4, 
                        border_radius=20)
        
        # Число по центру
        text = str(self.value)
        text_surf = self.big_font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(
            center=(self.box_x + self.box_width // 2, 
                   self.box_y + self.box_height // 2)
        )
        self.screen.blit(text_surf, text_rect)
        
        # Подсказка внизу
        hint = self.font.render("← вращай энкодер →", True, (180, 180, 180))
        hint_rect = hint.get_rect(center=(self.width // 2, self.height - 80))
        self.screen.blit(hint, hint_rect)
        
        # Пишем во framebuffer
        self.write_to_fb()
    
    def write_to_fb(self):
        # Конвертируем в RGB565
        rgb_array = np.frombuffer(
            pygame.image.tostring(self.screen, 'RGB'), 
            dtype=np.uint8
        ).reshape((self.height, self.width, 3))
        
        r = rgb_array[:,:,0].astype(np.uint32)
        g = rgb_array[:,:,1].astype(np.uint32)
        b = rgb_array[:,:,2].astype(np.uint32)
        
        # RGB565 конвертация
        rgb565 = ((r >> 3) << 11 | (g >> 2) << 5 | (b >> 3)).astype(np.uint16)
        
        # Добавляем padding если нужно
        if self.stride > self.width * 2:
            padding = np.zeros(
                (self.height, (self.stride - self.width * 2) // 2), 
                dtype=np.uint16
            )
            rgb565 = np.hstack([rgb565, padding])
        
        # Пишем в framebuffer
        self.fb.seek(0)
        self.fb.write(rgb565.tobytes())
        self.fb.flush()
    
    def close(self):
        if self.fb:
            self.fb.close()
        pygame.quit()

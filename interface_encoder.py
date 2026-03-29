#!/usr/bin/env python3
"""UI для энкодера — число по центру экрана"""
import pygame
import json
import os
import fcntl
import struct

class UI:
    def __init__(self, config_path):
        pygame.init()
        pygame.font.init()
        self.width = 1024
        self.height = 600
        self.use_fb = False
        self.fb = None
        
        os.system('setterm -blank 0 2>/dev/null')
        os.system('setterm -cursor off 2>/dev/null')
        
        try:
            self.fb = open('/dev/fb0', 'r+b')
            with open('/sys/class/graphics/fb0/virtual_size') as f:
                size = f.read().strip()
                self.width, self.height = map(int, size.split(','))
            try:
                with open('/sys/class/graphics/fb0/stride') as f:
                    self.stride = int(f.read().strip())
            except:
                self.stride = self.width * 3
            try:
                with open('/sys/class/graphics/fb0/bits_per_pixel') as f:
                    self.bpp = int(f.read().strip())
            except:
                self.bpp = 24
            self.screen = pygame.Surface((self.width, self.height))
            self.use_fb = True
        except:
            os.environ["SDL_VIDEODRIVER"] = "kmsdrm"
            self.screen = pygame.display.set_mode((self.width, self.height))
        
        pygame.display.set_caption('Encoder')
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
        
        self.write_to_fb()
    
    def write_to_fb(self):
        if not self.use_fb or not self.fb:
            pygame.display.flip()
            return
        try:
            import numpy as np
            rgb_array = np.frombuffer(
                pygame.image.tostring(self.screen, 'RGB'), 
                dtype=np.uint8
            ).reshape((self.height, self.width, 3))
            r = rgb_array[:,:,0].astype(np.uint32)
            g = rgb_array[:,:,1].astype(np.uint32)
            b = rgb_array[:,:,2].astype(np.uint32)
            rgb565 = ((r >> 3) << 11 | (g >> 2) << 5 | (b >> 3)).astype(np.uint16)
            if self.stride > self.width * 2:
                padding = np.zeros(
                    (self.height, (self.stride - self.width * 2) // 2), 
                    dtype=np.uint16
                )
                rgb565 = np.hstack([rgb565, padding])
            self.fb.seek(0)
            self.fb.write(rgb565.tobytes())
            self.fb.flush()
        except ImportError:
            self._write_fb_slow()
        except:
            pass
    
    def _write_fb_slow(self):
        rgb_data = pygame.image.tostring(self.screen, 'RGB')
        rgb565_data = bytearray()
        for i in range(0, len(rgb_data), 3):
            r, g, b = rgb_data[i], rgb_data[i+1], rgb_data[i+2]
            pixel = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
            rgb565_data.append(pixel & 0xFF)
            rgb565_data.append((pixel >> 8) & 0xFF)
        self.fb.seek(0)
        self.fb.write(bytes(rgb565_data))
        self.fb.flush()
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'quit'
                # Сброс значения пробелом
                if event.key == pygame.K_SPACE:
                    return 'reset'
        return None
    
    def close(self):
        os.system('setterm -cursor on 2>/dev/null')
        if self.fb:
            self.fb.close()
        pygame.quit()

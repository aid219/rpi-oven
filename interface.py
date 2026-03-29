#!/usr/bin/env python3
import pygame
import json
import time
import os
import fcntl
import struct
from PIL import Image


class TouchScreen:
    def __init__(self, screen_width=1024, screen_height=600):
        self.touch_fd = None
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.touch_max_x = 1023
        self.touch_max_y = 600
        self.last_touch = None
        self.touch_buffer = []
        try:
            self.touch_fd = open('/dev/input/event0', 'rb')
            flags = fcntl.fcntl(self.touch_fd, fcntl.F_GETFL)
            fcntl.fcntl(self.touch_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        except:
            pass
    
    def get_touch(self):
        if not self.touch_fd:
            return None
        try:
            while True:
                data = self.touch_fd.read(24)
                if not data or len(data) < 24:
                    break
                tv_sec, tv_usec, etype, code, value = struct.unpack('llHHi', data)
                if etype == 3:
                    if code == 53:
                        self.touch_buffer.append(('x', value))
                    elif code == 54:
                        self.touch_buffer.append(('y', value))
                    elif code == 57:
                        if value == -1:
                            if len(self.touch_buffer) >= 2:
                                x_val = next((v for t, v in self.touch_buffer if t == 'x'), 0)
                                y_val = next((v for t, v in self.touch_buffer if t == 'y'), 0)
                                self.touch_buffer = []
                                touch = {
                                    'x': int(x_val * self.screen_width / self.touch_max_x),
                                    'y': int(y_val * self.screen_height / self.touch_max_y)
                                }
                                self.last_touch = touch
                                return touch
                        else:
                            self.touch_buffer = []
                    elif code == 0:
                        self.touch_buffer.append(('x', value))
                    elif code == 1:
                        self.touch_buffer.append(('y', value))
                    elif code == 24:
                        if value == 0 and len(self.touch_buffer) >= 2:
                            x_val = next((v for t, v in self.touch_buffer if t == 'x'), 0)
                            y_val = next((v for t, v in self.touch_buffer if t == 'y'), 0)
                            self.touch_buffer = []
                            touch = {
                                'x': int(x_val * self.screen_width / self.touch_max_x),
                                'y': int(y_val * self.screen_height / self.touch_max_y)
                            }
                            self.last_touch = touch
                            return touch
        except BlockingIOError:
            pass
        except:
            pass
        return None
    
    def close(self):
        if self.touch_fd:
            self.touch_fd.close()


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
        self.touch = TouchScreen(self.width, self.height)
        pygame.display.set_caption('Oven Control')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        with open(config_path) as f:
            self.config = json.load(f)
        self.buttons = self.config.get('buttons', {})
        self.animations = self.config.get('animations', {})
        self.labels = self.config.get('labels', {})
        self.button_states = {}
        for name, btn in self.buttons.items():
            self.button_states[name] = btn.get('state', False)
    
    def set_button_state(self, name, state):
        if name in self.button_states:
            self.button_states[name] = state
            # Update button color
            if name in self.buttons:
                if state:
                    self.buttons[name]['color'] = [0, 180, 0]  # Green ON
                else:
                    self.buttons[name]['color'] = [180, 0, 0]  # Red OFF
    
    def draw_button(self, name, btn):
        x, y = btn['x'], btn['y']
        w, h = btn['width'], btn['height']
        state = self.button_states.get(name, False)
        # Green if ON, red if OFF
        if state:
            color = (0, 180, 0)
            border = (0, 255, 0)
        else:
            color = (180, 0, 0)
            border = (255, 0, 0)
        text = btn['text']
        pygame.draw.rect(self.screen, color, (x, y, w, h), border_radius=15)
        pygame.draw.rect(self.screen, border, (x, y, w, h), 3, border_radius=15)
        text_surf = self.big_font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(x + w//2, y + h//2))
        self.screen.blit(text_surf, text_rect)
    
    def draw_label(self, name, label):
        x, y = label['x'], label['y']
        font_size = label['font_size']
        text = label['text']
        font = pygame.font.Font(None, font_size)
        text_surf = font.render(text, True, (255, 255, 255))
        self.screen.blit(text_surf, (x, y))
    
    def draw(self):
        self.screen.fill((30, 30, 50))
        for name, btn in self.buttons.items():
            self.draw_button(name, btn)
        for name, label in self.labels.items():
            self.draw_label(name, label)
        self.write_to_fb()
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for name, btn in self.buttons.items():
                    if (btn['x'] <= x <= btn['x'] + btn['width'] and
                        btn['y'] <= y <= btn['y'] + btn['height']):
                        return btn['action']
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'quit'
        touch = self.touch.get_touch()
        if touch:
            x, y = touch['x'], touch['y']
            for name, btn in self.buttons.items():
                if (btn['x'] <= x <= btn['x'] + btn['width'] and
                    btn['y'] <= y <= btn['y'] + btn['height']):
                    return btn['action']
        return None
    
    def write_to_fb(self):
        if not self.use_fb or not self.fb:
            pygame.display.flip()
            return
        try:
            os.system('setterm -cursor off 2>/dev/null')
            import numpy as np
            rgb_array = np.frombuffer(pygame.image.tostring(self.screen, 'RGB'), dtype=np.uint8).reshape((self.height, self.width, 3))
            r = rgb_array[:,:,0].astype(np.uint32)
            g = rgb_array[:,:,1].astype(np.uint32)
            b = rgb_array[:,:,2].astype(np.uint32)
            rgb565 = ((r >> 3) << 11 | (g >> 2) << 5 | (b >> 3)).astype(np.uint16)
            if self.stride > self.width * 2:
                padding = np.zeros((self.height, (self.stride - self.width * 2) // 2), dtype=np.uint16)
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
    
    def close(self):
        os.system('setterm -cursor on 2>/dev/null')
        if self.fb:
            self.fb.close()
        if self.touch:
            self.touch.close()
        pygame.quit()

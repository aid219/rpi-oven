#!/usr/bin/env python3
"""Performance test"""
import time

# Test 1: GIF loading
print("Test 1: Loading GIF...")
from PIL import Image
start = time.time()
gif = Image.open('1.gif')
frames = []
for i in range(gif.n_frames):
    gif.seek(i)
    frames.append(gif.convert('RGB'))
print(f"Loaded {len(frames)} frames in {time.time()-start:.2f}s")

# Test 2: Convert to pygame surface
print("\nTest 2: Converting to pygame surfaces...")
import pygame
pygame.init()
start = time.time()
pg_frames = []
for f in frames:
    img = pygame.image.fromstring(f.tobytes(), f.size, 'RGB')
    pg_frames.append(img)
print(f"Converted in {time.time()-start:.2f}s")

# Test 3: Scale and blit
print("\nTest 3: Scale + blit (100 iterations)...")
screen = pygame.Surface((1024, 600))
start = time.time()
for i in range(100):
    frame = pg_frames[i % len(pg_frames)]
    scaled = pygame.transform.smoothscale(frame, (100, 100))
    screen.blit(scaled, (200, 100))
elapsed = time.time() - start
print(f"100 iterations in {elapsed:.2f}s ({100/elapsed:.1f} FPS)")

# Test 4: Framebuffer write
print("\nTest 4: FB write (10 iterations)...")
try:
    fb = open('/dev/fb0', 'wb')
    start = time.time()
    for i in range(10):
        data = pygame.image.tostring(screen, 'RGB')
        # Convert to BGR
        bgr = bytearray()
        for j in range(0, len(data), 3):
            bgr.extend([data[j+2], data[j+1], data[j]])
        fb.seek(0)
        fb.write(bytes(bgr))
    elapsed = time.time() - start
    print(f"10 FB writes in {elapsed:.2f}s ({10/elapsed:.1f} FPS)")
    fb.close()
except Exception as e:
    print(f"FB error: {e}")

print("\nDone!")

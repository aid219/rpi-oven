#!/usr/bin/env python3
import os, sys, math, time, signal, struct
import pygame

WIDTH, HEIGHT = 320, 480
FPS_TARGET = 30

class Ball:
    def __init__(s,x,y,r,c,sx,sy):
        s.x,s.y,s.r,s.c,s.sx,s.sy = x,y,r,c,sx,sy
    def update(s,w,h):
        s.x += s.sx; s.y += s.sy
        if s.x-s.r<0 or s.x+s.r>w: s.sx = -s.sx; s.x = max(s.r,min(s.x,w-s.r))
        if s.y-s.r<0 or s.y+s.r>h: s.sy = -s.sy; s.y = max(s.r,min(s.y,h-s.r))

def main():
    running = True
    def stop(sig,frm):
        nonlocal running
        print('\nStop...')
        running = False
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    
    pygame.init()
    screen = pygame.Surface((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    balls = [
        Ball(60,60,25,(255,0,0),3,2),
        Ball(160,100,30,(0,255,0),-2,3),
        Ball(260,150,20,(0,0,255),4,-2),
        Ball(100,200,22,(255,255,0),-3,-3),
        Ball(200,250,28,(0,255,255),2,-4)
    ]
    
    grid = pygame.Surface((WIDTH,HEIGHT))
    grid.fill((0,0,0))
    for x in range(0, WIDTH, 40):
        pygame.draw.line(grid, (40,40,40), (x,0), (x,HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(grid, (40,40,40), (0,y), (WIDTH,y))
    
    angle = 0
    print(f'Start: {WIDTH}x{HEIGHT} @ {FPS_TARGET}FPS. Ctrl+C=stop')
    
    try:
        fb = open('/dev/fb0', 'wb')
        use_fb = True
    except Exception as e:
        print(f'No fb0: {e}')
        use_fb = False
        os.environ['SDL_VIDEODRIVER'] = 'KMSDRM'
        display = pygame.display.set_mode((WIDTH,HEIGHT), pygame.FULLSCREEN)
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                    running = False
            
            for b in balls:
                b.update(WIDTH, HEIGHT)
            angle += 0.05
            
            screen.blit(grid, (0,0))
            for b in balls:
                pygame.draw.circle(screen, b.c, (int(b.x), int(b.y)), b.r)
            
            r = int(127 + 127*math.sin(angle))
            g = int(127 + 127*math.sin(angle+2))
            bcol = int(127 + 127*math.sin(angle+4))
            fps_txt = font.render(f'FPS:{int(clock.get_fps())}', True, (r,g,bcol))
            screen.blit(fps_txt, (10,10))
            
            if use_fb:
                fb.seek(0)
                fb.write(pygame.image.tostring(screen, 'RGB'))
                fb.flush()
            else:
                display.blit(screen, (0,0))
                pygame.display.flip()
            
            clock.tick(FPS_TARGET)
            
            frame_count += 1
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                if elapsed > 0:
                    print(f'FPS: {frame_count/elapsed:.1f}')
                start_time = time.time()
                frame_count = 0
    
    finally:
        if use_fb:
            fb.close()
        pygame.quit()
        print('Stopped')

if __name__ == '__main__':
    main()

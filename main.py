#!/usr/bin/env python3
import os, sys, signal, time, pygame

PID_FILE = '/tmp/oven.pid'
PIN_NUMBERS = {'toggle_1': 17, 'toggle_2': 27, 'toggle_3': 22, 'toggle_4': 5, 'toggle_5': 6, 'toggle_6': 13}
button_states = {k: False for k in PIN_NUMBERS}

def cleanup():
    try:
        import RPi.GPIO as GPIO
        for pin in PIN_NUMBERS.values(): GPIO.output(pin, GPIO.LOW)
        GPIO.cleanup()
    except: pass
    try: os.remove(PID_FILE)
    except: pass
    sys.exit(0)

signal.signal(signal.SIGINT, lambda s,f: cleanup())
signal.signal(signal.SIGTERM, lambda s,f: cleanup())

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in PIN_NUMBERS.values(): GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
except: pass

with open(PID_FILE, 'w') as f: f.write(str(os.getpid()))

from interface import UI, TouchScreen
ui = UI('config.json')
last_event = time.time()

while True:
    if time.time() - last_event > 10:
        try:
            ui.touch.close()
            ui.touch = TouchScreen(ui.width, ui.height)
        except: pass
        last_event = time.time()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: cleanup()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: cleanup()
    
    touch = ui.touch.get_touch()
    if touch:
        x, y = touch['x'], touch['y']
        for name, btn in ui.buttons.items():
            if btn['x'] <= x <= btn['x'] + btn['width'] and btn['y'] <= y <= btn['y'] + btn['height']:
                action = btn['action']
                if action.startswith('toggle_'):
                    button_states[action] = not button_states[action]
                    ui.set_button_state(action.replace('toggle_', 'btn'), button_states[action])
                    try:
                        import RPi.GPIO as GPIO
                        GPIO.output(PIN_NUMBERS[action], GPIO.HIGH if button_states[action] else GPIO.LOW)
                    except: pass
                last_event = time.time()
    
    ui.draw()
    ui.clock.tick(30)

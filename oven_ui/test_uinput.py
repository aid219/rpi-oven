#!/usr/bin/env python3
import uinput
import time

print('Creating device...')
events = (uinput.BTN_LEFT, uinput.ABS_X, uinput.ABS_Y)
device = uinput.Device(events)
print('Device created!')
time.sleep(5)
device.destroy()
print('Done')

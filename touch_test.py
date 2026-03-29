#!/usr/bin/env python3
"""Тач-тест для event0"""
import struct, fcntl, os, time

fd = open('/dev/input/event0', 'rb')
flags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

print('event0 opened. Коснись экрана 3 раза:')

for i in range(300):  # ~10 сек
    try:
        data = fd.read(24)
        if data:
            t,_,e,c,v = struct.unpack('llHHi', data)
            if e == 3:
                print(f'code={c} val={v}')
    except: pass
    time.sleep(0.03)

fd.close()
print('done')

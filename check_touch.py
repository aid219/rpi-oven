#!/usr/bin/env python3
import struct, fcntl, os, time

fd = open('/dev/input/event0', 'rb')
flags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

print('Коснись экрана:')

for i in range(200):
    try:
        data = fd.read(24)
        if data:
            _,_,e,c,v = struct.unpack('llHHi', data)
            if e == 3:
                print(f'code={c} val={v}')
    except: pass
    time.sleep(0.03)

fd.close()

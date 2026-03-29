#!/usr/bin/env python3
"""Проверка event0 (QDtech сенсор)"""
import struct, fcntl, os, time

print("=" * 50)
print("QDTECH ТЕСТ: Коснись экрана")
print("=" * 50)

fd = open('/dev/input/event0', 'rb')
flags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

print("Жду касаний... (Ctrl+C для выхода)")

try:
    while True:
        try:
            data = fd.read(24)
            if data and len(data) == 24:
                tv_sec, tv_usec, etype, code, value = struct.unpack('llHHi', data)
                if etype == 3:  # EV_ABS
                    label = {0: 'X', 1: 'Y', 24: 'PRESS', 47: 'SLOT'}.get(code, f'C{code}')
                    print(f"{label}: {value}")
        except BlockingIOError:
            time.sleep(0.05)
except KeyboardInterrupt:
    pass
finally:
    fd.close()

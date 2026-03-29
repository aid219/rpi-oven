#!/usr/bin/env python3
"""Простой тест сенсора - запусти и коснись экрана"""
import struct, fcntl, os, time

print("=" * 50)
print("ТОЧ-ТЕСТ: Коснись экрана и смотри что будет")
print("=" * 50)
print()

fd = open('/dev/input/event4', 'rb')
flags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

print("Жду касаний... (нажми Ctrl+C для выхода)")
print()

count = 0
start = time.time()

try:
    while True:
        try:
            data = fd.read(24)
            if data and len(data) == 24:
                tv_sec, tv_usec, etype, code, value = struct.unpack('llHHi', data)
                count += 1
                
                # Показываем только ABS события
                if etype == 3:
                    label = {0: 'X', 1: 'Y', 24: 'PRESS'}.get(code, str(code))
                    print(f"[{count}] {label}: {value}")
                
        except BlockingIOError:
            time.sleep(0.05)
            
except KeyboardInterrupt:
    elapsed = time.time() - start
    print(f"\nГотово! За {elapsed:.1f} сек получено {count} событий")
finally:
    fd.close()

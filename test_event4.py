#!/usr/bin/env python3
import struct
import fcntl
import os

print("Opening /dev/input/event4...")
fd = open('/dev/input/event4', 'rb')

# Non-blocking
flags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

print("Touch screen and watch values (Ctrl+C to exit):\n")

try:
    while True:
        try:
            data = fd.read(24)
            if data and len(data) == 24:
                tv_sec, tv_usec, etype, code, value = struct.unpack('llHHi', data)
                if etype == 3:  # EV_ABS
                    if code == 0:
                        print(f"X = {value}")
                    elif code == 1:
                        print(f"Y = {value}")
                    elif code == 24:
                        print(f"Pressure = {value}")
        except BlockingIOError:
            pass
except KeyboardInterrupt:
    print("\nDone!")
finally:
    fd.close()

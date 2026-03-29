#!/usr/bin/env python3
import struct, fcntl, os

fd = open('/dev/input/event4', 'rb')
flags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

print("Touch screen for 10 seconds, then Ctrl+C:\n")

try:
    for i in range(500):  # ~10 секунд
        try:
            data = fd.read(24)
            if data and len(data) == 24:
                tv_sec, tv_usec, etype, code, value = struct.unpack('llHHi', data)
                print(f"type={etype} code={code} value={value}")
        except BlockingIOError:
            pass
        except Exception as e:
            print(f"Error: {e}")
except KeyboardInterrupt:
    pass
finally:
    fd.close()

print("\nDone!")

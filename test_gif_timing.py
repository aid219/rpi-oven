#!/usr/bin/env python3
"""GIF Timing Test"""
import time

print("Запуск main.py на 10 секунд...")
print("Через 3 секунды коснись GIF на экране")
print()

import subprocess
proc = subprocess.Popen(['python3', 'main.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

time.sleep(10)
proc.terminate()

print("\n\n=== ЛОГ GIF ===")
import os
with open('/tmp/oven.log') as f:
    for line in f:
        if 'GIF heart' in line or 'frame=' in line:
            print(line.strip())

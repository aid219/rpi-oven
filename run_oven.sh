#!/bin/bash
# Запуск Oven Control в фоне

# Остановить если запущен
pkill -f "python3 main.py" 2>/dev/null
sleep 1

# Переключиться на VT2
sudo chvt 2

# Запустить в фоне
cd ~/oven
export SDL_VIDEODRIVER=fbcon
export SDL_FBDEV=/dev/fb0
nohup python3 main.py > /dev/null 2>&1 &

# Вернуться на VT1
sleep 2
sudo chvt 1

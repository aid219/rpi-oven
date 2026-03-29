#!/bin/bash
# Запускаем приложение в фоне на VT2
cd ~/oven
export SDL_VIDEODRIVER=kmsdrm
export SDL_KMSDRM_DEVICE=/dev/dri/card0
nohup python3 main.py > /tmp/oven.log 2>&1 &

# Переключаемся на VT2 через 2 секунды
sleep 2
sudo chvt 2

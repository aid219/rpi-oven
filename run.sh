#!/bin/bash
# Запуск Oven Control на отдельной консоли (TTY2)

# Остановить если запущен
pkill -9 -f "python3.*main.py" 2>/dev/null
rm -f /tmp/oven.pid
sleep 1

# Переключиться на TTY2 и запустить там
sudo chvt 2
sleep 1

# Запуск на TTY2
sudo -u qummy bash -c '
    export DISPLAY=:0
    cd /home/qummy/oven
    python3 main.py
' &

# Вернуться на TTY1 (где ты работаешь)
sleep 3
sudo chvt 1

echo "Oven Control запущен на TTY2"
echo "Чтобы остановить: ~/oven/stop.sh"
echo "Чтобы перейти к приложению: sudo chvt 2"
echo "Чтобы вернуться обратно: sudo chvt 1"

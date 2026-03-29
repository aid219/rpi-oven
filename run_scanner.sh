#!/bin/bash
# Запуск сканера QR-кодов на отдельной консоли (TTY2)

# Остановить если запущен
pkill -9 -f "python3.*main_scanner.py" 2>/dev/null
rm -f /tmp/scanner.pid
sleep 1

# Переключиться на TTY2 и запустить там
sudo chvt 2
sleep 1

# Запуск на TTY2
sudo -u qummy bash -c '
    cd /home/qummy/oven
    python3 main_scanner.py
' &

# Вернуться на TTY1 (где ты работаешь)
sleep 3
sudo chvt 1

echo "QR Scanner запущен на TTY2"
echo "Чтобы остановить: pkill -f main_scanner.py"
echo "Чтобы перейти к приложению: sudo chvt 2"
echo "Чтобы вернуться обратно: sudo chvt 1"

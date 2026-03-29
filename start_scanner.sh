#!/bin/bash
# Запуск UART сканера с исправлением прав

# Исправляем права на порт
sudo chmod 660 /dev/ttyS0 2>/dev/null
sudo chown root:dialout /dev/ttyS0 2>/dev/null

# Запускаем сканер
cd /home/qummy/oven
python3 uart_scanner.py

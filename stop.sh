#!/bin/bash
# Остановить Oven Control через SSH
if [ -f /tmp/oven.pid ]; then
    PID=$(cat /tmp/oven.pid)
    kill $PID 2>/dev/null
    sleep 1
    # Если не убился - убить силой
    kill -9 $PID 2>/dev/null
    rm -f /tmp/oven.pid
    echo "Oven Control stopped"
else
    # Если PID файла нет - найти и убить процесс
    pkill -9 -f "python3.*main.py" 2>/dev/null
    echo "Oven Control stopped (force)"
fi

#!/bin/bash
# Oven UI - безопасный запуск

SCRIPT_DIR="/home/qummy/oven_ui"
DAEMON_SCRIPT="$SCRIPT_DIR/daemon/touch_daemon.py"
UI_SCRIPT="$SCRIPT_DIR/ui/ui_debug.py"
PID_FILE="$SCRIPT_DIR/daemon.pid"

# Сохраняем настройки терминала
stty -g > /tmp/term_settings 2>/dev/null

cleanup() {
    echo ""
    echo "Stopping..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        sudo kill $PID 2>/dev/null
        sudo kill -9 $PID 2>/dev/null
        rm -f "$PID_FILE"
    fi
    
    sudo pkill -9 -f "touch_daemon.py" 2>/dev/null
    sudo pkill -9 -f "ui_debug.py" 2>/dev/null
    rm -f /tmp/touch_coords.dat
    
    # Восстанавливаем терминал
    if [ -f /tmp/term_settings ]; then
        stty $(cat /tmp/term_settings) 2>/dev/null
        rm -f /tmp/term_settings
    fi
    
    echo "Done"
    echo ""
}

trap cleanup EXIT INT TERM

echo "========================================"
echo "OVEN UI"
echo "========================================"
echo ""

# Остановка старого
echo "Stopping old processes..."
sudo pkill -9 -f "touch_daemon.py" 2>/dev/null
sudo pkill -9 -f "ui_debug.py" 2>/dev/null
sleep 2

# Запуск демона
echo "Starting daemon..."
cd "$SCRIPT_DIR/daemon"
sudo python3 "$DAEMON_SCRIPT" &
echo $! > "$PID_FILE"
sleep 2

# Проверка
if [ ! -e /tmp/touch_coords.dat ]; then
    echo "ERROR: Daemon failed!"
    exit 1
fi
echo "Daemon ready"
echo ""

# Запуск UI
echo "Starting UI..."
echo "Touch the button, ESC to exit"
echo "========================================"
cd "$SCRIPT_DIR/ui"
sudo python3 "$UI_SCRIPT"

echo ""
echo "========================================"
echo "Finished"

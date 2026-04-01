#!/bin/bash
# Установка systemd сервиса для Kivy Oven UI

SERVICE_FILE="kivy-oven-ui.service"
SERVICE_DEST="/etc/systemd/system/$SERVICE_FILE"

echo "Installing Kivy Oven UI systemd service..."

# Копирование файла сервиса
sudo cp $SERVICE_FILE $SERVICE_DEST

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable $SERVICE_FILE

echo ""
echo "Service installed successfully!"
echo ""
echo "Useful commands:"
echo "  sudo systemctl start $SERVICE_FILE     - Start service"
echo "  sudo systemctl stop $SERVICE_FILE      - Stop service"
echo "  sudo systemctl status $SERVICE_FILE    - Check status"
echo "  sudo systemctl disable $SERVICE_FILE   - Disable auto-start"
echo "  journalctl -u $SERVICE_FILE -f         - View logs"

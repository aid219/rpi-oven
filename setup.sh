#!/bin/bash
# Oven Control - установка на Raspberry Pi

echo "=== Oven Control Setup ==="

# Создаём папку
mkdir -p ~/oven

# Устанавливаем зависимости
echo "Installing dependencies..."
pip install pygame pillow

# Копируем файлы (если запускаем из папки с проектом)
if [ -f "main.py" ]; then
    cp main.py interface.py config.json 1.gif ~/oven/
fi

echo ""
echo "=== Готово! ==="
echo "Для запуска выполни:"
echo "  cd ~/oven"
echo "  export SDL_VIDEODRIVER=kmsdrm"
echo "  python3 main.py"

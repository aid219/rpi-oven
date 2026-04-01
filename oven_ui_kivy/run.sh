#!/bin/bash
# Запуск Kivy UI приложения

cd /home/qummy/rpi-oven/oven_ui_kivy

# Настройка переменных окружения
export KIVY_VIDEO=gl
export KIVY_LOG_LEVEL=info

# Запуск приложения
python3 main.py

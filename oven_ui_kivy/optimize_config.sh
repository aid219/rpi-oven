#!/bin/bash
# Оптимизация config.txt для максимального FPS SPI дисплея

CONFIG="/boot/firmware/config.txt"

echo "=== Оптимизация config.txt для SPI ==="

# Создаём резервную копию
sudo cp $CONFIG ${CONFIG}.backup

echo "Бэкап создан: ${CONFIG}.backup"

# Читаем текущий config
cat $CONFIG | grep -v "^dtoverlay=vc4-kms" | grep -v "^max_framebuffers" > /tmp/config_optimized.txt

# Добавляем оптимизации
cat >> /tmp/config_optimized.txt << 'EOF'

# === OPTIMIZATIONS FOR SPI DISPLAY ===
# Отключаем медленный DRM
dtoverlay=vc4-kms-v3d,cma-16
max_framebuffers=1

# Увеличиваем частоту SPI (максимум для ST7796U = 62MHz)
dtoverlay=mipi-dbi-spi,spi0-0,speed=62000000

# Разгон ядра (осторожно!)
core_freq=500
core_freq_turbo=550

# Уменьшаем задержки
gpu_freq=300

# Оптимизация памяти
gpu_mem=128
EOF

# Копируем оптимизированный config
sudo cp /tmp/config_optimized.txt $CONFIG

echo ""
echo "=== Изменения внесены ==="
echo ""
echo "Новые настройки:"
grep -E '(vc4-kms|core_freq|gpu_freq|speed=)' $CONFIG
echo ""
echo "Требуется перезагрузка!"
echo "sudo reboot"

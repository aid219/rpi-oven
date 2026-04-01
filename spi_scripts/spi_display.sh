#!/bin/bash
# Скрипты для SPI дисплея ST7796U 320x480

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$1" in
    video|1|mp4)
        echo "Запуск видео 1.mp4..."
        sudo python3 "$SCRIPT_DIR/play_video_fast.py" "$SCRIPT_DIR/1.mp4"
        ;;
    gif|2|anim)
        echo "Запуск анимации 2.gif..."
        sudo python3 "$SCRIPT_DIR/play_gif_final.py" "$SCRIPT_DIR/2.gif"
        ;;
    test|fps)
        echo "Запуск теста FPS..."
        sudo python3 "$SCRIPT_DIR/simple_spi_anim.py"
        ;;
    stop|kill)
        echo "Остановка всех скриптов..."
        sudo pkill -f play_video
        sudo pkill -f play_gif
        sudo pkill -f simple_spi
        echo "Остановлено"
        ;;
    bg)
        # Запуск в фоне
        shift
        if [ "$1" = "video" ] || [ "$1" = "1" ]; then
            echo "Запуск видео в фоне..."
            sudo python3 "$SCRIPT_DIR/play_video_fast.py" "$SCRIPT_DIR/1.mp4" &
        elif [ "$1" = "gif" ] || [ "$1" = "2" ]; then
            echo "Запуск GIF в фоне..."
            sudo python3 "$SCRIPT_DIR/play_gif_final.py" "$SCRIPT_DIR/2.gif" &
        fi
        echo "Запущено в фоне (PID: $!)"
        echo "Для остановки: sudo pkill -f play_video или sudo pkill -f play_gif"
        ;;
    *)
        echo "SPI Display Scripts"
        echo ""
        echo "Использование:"
        echo "  $0 video     - Запустить видео 1.mp4"
        echo "  $0 gif       - Запустить GIF анимацию 2.gif"
        echo "  $0 test      - Запуск теста FPS"
        echo "  $0 stop      - Остановить все скрипты"
        echo ""
        echo "  $0 bg video  - Запустить видео в фоне"
        echo "  $0 bg gif    - Запустить GIF в фоне"
        echo ""
        echo "Для остановки: Ctrl+C или '$0 stop'"
        ;;
esac

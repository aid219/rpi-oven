# 📡 Подключение UART сканера QR-кодов

## 🔌 Схема подключения к Raspberry Pi Zero 2 W

```
Сканер          Raspberry Pi Zero 2 W
------          ---------------------
VCC    ────────  5V (Pin 2 или 4)
GND    ────────  GND (Pin 6)
TX     ────────  GPIO 14 / RXD (Pin 10)
RX     ────────  GPIO 15 / TXD (Pin 8)
```

⚠️ **Важно:** Соединяйте **TX сканера → RX Raspberry Pi** и **RX сканера → TX Raspberry Pi**

---

## 🔧 Настройка Raspberry Pi

### 1. Включить UART

Отредактируйте `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

Добавьте/проверьте строки:
```
enable_uart=1
dtoverlay=disable-bt
```

### 2. Отключить консоль на UART (опционально)

Отредактируйте `/boot/cmdline.txt`:
```bash
sudo nano /boot/cmdline.txt
```

Удалите `console=serial0,115200` если есть.

### 3. Перезагрузка
```bash
sudo reboot
```

---

## 🧪 Проверка подключения

### 1. Проверить доступные UART устройства:
```bash
ls -l /dev/serial*
```

Должно появиться `/dev/serial0` → `/dev/ttyAMA0`

### 2. Проверить порт:
```bash
ls -l /dev/ttyAMA0
```

### 3. Установить зависимости:
```bash
pip install -r requirements.txt
```

---

## 🚀 Запуск

### Вариант 1: Через скрипт
```bash
chmod +x run_scanner.sh
./run_scanner.sh
```

### Вариант 2: Напрямую
```bash
python3 main_scanner.py
```

### Остановка
```bash
pkill -f main_scanner.py
```

---

## 📋 Параметры сканера по умолчанию

| Параметр | Значение |
|----------|----------|
| Порт | `/dev/serial0` |
| Baud rate | `9600` |
| Timeout | `1 сек` |

---

## 🔍 Если не работает

1. **Проверьте подключение проводов** (TX→RX, RX→TX)
2. **Проверьте права доступа:**
   ```bash
   sudo usermod -a -G dialout qummy
   ```
3. **Попробуйте другой порт** в `main_scanner.py`:
   - `/dev/ttyAMA0`
   - `/dev/ttyS0`
   - `/dev/serial0`

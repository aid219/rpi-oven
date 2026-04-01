# Архитектура: Main Application + Daemon'ы

## 📋 Обзор

Микросервисная архитектура для embedded-системы на Raspberry Pi.

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN APPLICATION                         │
│                   (UI + Business Logic)                     │
│                                                             │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│   │Touch Client │ │Scanner      │ │Player       │          │
│   │             │ │Client       │ │Client       │          │
│   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘          │
└──────────┼───────────────┼───────────────┼─────────────────┘
           │               │               │
           │ Unix Sockets  │ Unix Sockets  │ Unix Sockets
           │               │               │
           ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  touch_daemon   │ │ scanner_daemon  │ │ player_daemon   │
│  (I2C Touch)    │ │ (UART Scanner)  │ │ (Audio/VLC)     │
│                 │ │                 │ │                 │
│  /tmp/touch.sock│ │ /tmp/scan.sock  │ │ /tmp/player.sock│
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         ▼                   ▼                   ▼
    I2C Device           UART Device         ALSA/VLC
```

---

## 🎯 Преимущества архитектуры

| Преимущество | Описание |
|--------------|----------|
| **Изоляция сбоев** | Если `touch_daemon` упал → main продолжает работать |
| **Независимые циклы** | Каждый демон работает в своём темпе (50 Гц, 10 Гц, 60 FPS) |
| **Легкое тестирование** | Можно тестировать демоны отдельно через `nc -U` |
| **Перезапуск на лету** | Можно перезапустить демон без перезапуска main |
| **Разделение ответственности** | Каждый демон отвечает за своё устройство |
| **Масштабируемость** | Легко добавить новый демон (RGB, GPIO, и т.д.) |

---

## 📁 Структура проекта

```
oven_ui/
├── daemon_base.py              # Базовый класс для всех демонов
├── daemon_client.py            # Клиент для подключения к демонам
│
├── daemons/
│   ├── __init__.py
│   ├── touch_daemon.py         # I2C тачскрин (0x38)
│   ├── scanner_daemon.py       # UART сканер штрих-кодов
│   ├── player_daemon.py        # Аудио плеер (VLC/ALSA)
│   └── encoder_daemon.py       # GPIO энкодер + кнопки
│
├── main.py                     # Основное приложение (UI + логика)
│
├── systemd/
│   ├── touch-daemon.service
│   ├── scanner-daemon.service
│   ├── player-daemon.service
│   ├── encoder-daemon.service
│   └── main-app.service
│
├── config/
│   └── daemons.json            # Конфигурация демонов
│
└── logs/
    ├── touch_daemon.log
    ├── scanner_daemon.log
    ├── player_daemon.log
    └── encoder_daemon.log
```

---

## 🔌 Протокол общения (JSON)

### Формат сообщений

```json
// Команда от клиента к демону
{"cmd": "play", "track": "song.mp3"}

// Событие от демона к клиенту
{"cmd": "touch", "x": 100, "y": 200, "pressed": true}

// Ответ на запрос
{"status": "ok", "volume": 50}
```

### Стандартные команды

| Команда | Описание | Ответ |
|---------|----------|-------|
| `ping` | Проверка связи | `{"status": "pong"}` |
| `get_status` | Получить статус демона | `{"status": "ok", ...}` |
| `reset` | Перезапустить демон | `{"status": "reset_complete"}` |

### Команды touch_daemon

| Команда | Параметры | Событие |
|---------|-----------|---------|
| `calibrate` | - | `{"cmd": "touch", "x": N, "y": N, "pressed": bool}` |

### Команды scanner_daemon

| Команда | Параметры | Событие |
|---------|-----------|---------|
| `get_config` | - | `{"cmd": "scan", "data": "4829384756"}` |

### Команды player_daemon

| Команда | Параметры | Событие |
|---------|-----------|---------|
| `play` | `track: str` | `{"cmd": "track_ended", "track": str}` |
| `pause` | - | - |
| `stop` | - | - |
| `volume` | `level: int` | - |

### Команды encoder_daemon

| Команда | Параметры | Событие |
|---------|-----------|---------|
| - | - | `{"cmd": "encoder", "direction": "cw\|ccw"}` |
| - | - | `{"cmd": "button", "pressed": bool, "pin": int}` |

---

## 🏗 Реализация

### Шаг 1: Базовый класс (`daemon_base.py`)

**Класс `DaemonConfig`** — конфигурация демона:
- `name` — имя демона
- `socket_path` — путь к сокету (например, `/tmp/touch.sock`)
- `pid_file` — PID файл (например, `/var/run/touch_daemon.pid`)
- `log_file` — лог файл (например, `/var/log/touch_daemon.log`)
- `poll_interval` — интервал опроса железа (сек)
- `reconnect_delay` — задержка переподключения (сек)

**Класс `BaseDaemon`** — базовый класс для всех демонов:
- `_setup_logging()` — настройка логирования
- `_setup_signal_handlers()` — обработка SIGTERM, SIGINT, SIGHUP
- `_write_pid()` / `_remove_pid()` — управление PID файлом
- `setup_socket()` — создание Unix сокета
- `cleanup_socket()` — очистка сокета
- `send_to_client()` — отправка сообщения клиенту
- `process_client_data()` — обработка данных от клиента
- `run()` — основной цикл демона
- `shutdown()` — корректная остановка

**Абстрактные методы (переопределяются в наследниках):**
- `handle_message(message)` — обработка команд от клиента
- `poll_hardware()` — опрос оборудования

**Класс `DaemonClient`** — клиент для подключения к демону:
- `connect()` — подключиться к демону
- `disconnect()` — отключиться от демона
- `send(cmd, **kwargs)` — отправить команду (без ожидания ответа)
- `request(cmd, **kwargs)` — отправить команду и ждать ответ
- `poll()` — получить события от демона (неблокирующий)

---

### Шаг 2: Демоны

#### `touch_daemon.py` — Тачскрин

**Оборудование:**
- I2C адрес: `0x38`
- Reset pin: GPIO 27
- Частота опроса: 50 Гц (0.02 сек)

**Логика:**
1. Reset при старте
2. Чтение регистра 0x02 (статус касания)
3. При касании: чтение координат (регистры 0x03-0x06)
4. Отправка событий только при изменении

**События:**
```json
{"cmd": "touch", "x": 100, "y": 200, "pressed": true}
{"cmd": "touch", "x": 100, "y": 200, "pressed": false}
```

---

#### `scanner_daemon.py` — Сканер штрих-кодов

**Оборудование:**
- UART: `/dev/ttyUSB0`
- Baudrate: 9600
- Частота опроса: 10 Гц (0.1 сек)

**Логика:**
1. Чтение из UART
2. Буферизация до `\n`
3. Отправка штрих-кода при получении

**События:**
```json
{"cmd": "scan", "data": "4829384756", "timestamp": 1234567890.123}
```

---

#### `player_daemon.py` — Аудио плеер

**Оборудование:**
- VLC / ALSA
- Частота опроса: 2 Гц (0.5 сек)

**Команды:**
- `play` + `track` → запуск трека
- `pause` → пауза/продолжить
- `stop` → остановка
- `volume` + `level` → громкость 0-100
- `get_status` → текущий статус

**События:**
```json
{"cmd": "track_ended", "track": "song.mp3"}
```

---

#### `encoder_daemon.py` — Энкодер и кнопки

**Оборудование:**
- Encoder A: GPIO 5
- Encoder B: GPIO 6
- Button: GPIO 13
- Частота опроса: 20 Гц (0.05 сек)

**Логика:**
1. Опрос состояния GPIO
2. Определение направления вращения (A/B фазы)
3. Детектирование нажатия кнопки

**События:**
```json
{"cmd": "encoder", "direction": "cw"}      // по часовой
{"cmd": "encoder", "direction": "ccw"}     // против часовой
{"cmd": "button", "pressed": true, "pin": 13}
{"cmd": "button", "pressed": false, "pin": 13}
```

---

### Шаг 3: Основное приложение (`main.py`)

**Класс `DaemonManager`** — менеджер подключений:
- `register_daemon(name, socket_path)` — зарегистрировать демон
- `on_event(name, callback)` — подписка на события
- `connect_all()` — подключение ко всем демонам
- `send(daemon, cmd, **kwargs)` — отправка команды
- `request(daemon, cmd, **kwargs)` — запрос с ответом
- `poll_all()` — опрос всех демонов

**Класс `MainApp`** — основное приложение:
- Регистрация всех демонов
- Подписка на события (callback'и)
- Основной цикл (60 FPS)
- Обработка событий от демонов

**Пример callback'ов:**
```python
def on_touch(event):
    x, y, pressed = event['x'], event['y'], event['pressed']
    # Обновление UI

def on_scan(event):
    barcode = event['data']
    # Поиск товара

def on_encoder(event):
    direction = event['direction']
    # Скролл меню

def on_button(event):
    pressed = event['pressed']
    # Выбор пункта
```

---

### Шаг 4: Systemd сервисы

**Пример: `/etc/systemd/system/touch-daemon.service`**

```ini
[Unit]
Description=Touch Daemon
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/dmitrii/Documents/dev/yy/rpi-oven/oven_ui/daemons/touch_daemon.py
Restart=always
RestartSec=3
User=dmitrii
WorkingDirectory=/home/dmitrii/Documents/dev/yy/rpi-oven/oven_ui

[Install]
WantedBy=multi-user.target
```

**Команды управления:**
```bash
# Перезагрузка конфига
sudo systemctl daemon-reload

# Включить автозапуск
sudo systemctl enable touch-daemon

# Запустить / остановить / перезапустить
sudo systemctl start touch-daemon
sudo systemctl stop touch-daemon
sudo systemctl restart touch-daemon

# Проверить статус
sudo systemctl status touch-daemon

# Посмотреть логи
journalctl -u touch-daemon -f
```

---

## 🧪 Тестирование

### Тестирование демонов по отдельности

```bash
# Запустить демон
python3 daemons/touch_daemon.py &

# Подключиться через netcat
nc -U /tmp/touch.sock

# Отправить команду
echo '{"cmd": "ping"}' | nc -U /tmp/touch.sock

# Посмотреть PID
cat /var/run/touch_daemon.pid
```

### Тестирование основного приложения

```bash
# Запустить все демоны
python3 daemons/touch_daemon.py &
python3 daemons/scanner_daemon.py &
python3 daemons/player_daemon.py &
python3 daemons/encoder_daemon.py &

# Запустить main
python3 main.py
```

### Проверка логов

```bash
tail -f /var/log/touch_daemon.log
tail -f /var/log/scanner_daemon.log
tail -f /var/log/player_daemon.log
tail -f /var/log/encoder_daemon.log
```

---

## 📝 План реализации

### Этап 1: Базовая инфраструктура
- [ ] Создать `daemon_base.py` (базовый класс + клиент)
- [ ] Протестировать базовый класс на простом примере

### Этап 2: Переписать демоны
- [ ] `touch_daemon.py` (на базе `BaseDaemon`)
- [ ] `scanner_daemon.py` (на базе `BaseDaemon`)
- [ ] `player_daemon.py` (на базе `BaseDaemon`)
- [ ] `encoder_daemon.py` (на базе `BaseDaemon`)

### Этап 3: Основное приложение
- [ ] Создать `main.py` с `DaemonManager`
- [ ] Реализовать callback'и для всех демонов
- [ ] Протестировать связь main ↔ демоны

### Этап 4: Systemd и production
- [ ] Создать `.service` файлы для всех демонов
- [ ] Создать `.service` файл для main приложения
- [ ] Настроить автозапуск
- [ ] Настроить логирование через `journalctl`

### Этап 5: Документация и тесты
- [ ] Написать документацию по протоколу
- [ ] Создать тесты для каждого демона
- [ ] Создать тесты для `main.py`

---

## ⚠️ Важные замечания

### 1. Безопасность сокетов
```bash
# Права на сокет (0o666 — все могут подключиться)
os.chmod(SOCKET_PATH, 0o666)

# Если нужно ограничить доступ:
os.chmod(SOCKET_PATH, 0o660)  # только владелец и группа
```

### 2. Обработка отключений
- Main должен автоматически переподключаться к демонам
- Демоны должны корректно обрабатывать отключение клиента

### 3. Graceful shutdown
```python
# При SIGTERM/SIGINT
def shutdown(self):
    self.running = False
    cleanup_socket()
    remove_pid()
```

### 4. Логирование
- Каждый демон пишет в свой лог файл
- Main пишет в свой лог файл
- Использовать `logging` модуль с уровнями (DEBUG, INFO, WARNING, ERROR)

### 5. Конфигурация
- Вынести конфигурацию в отдельный файл (`config/daemons.json`)
- Пути к сокетам, PID файлам, лог файлам
- Интервалы опроса, параметры устройств

---

## 🔗 Полезные ссылки

- [Unix Domain Sockets](https://man7.org/linux/man-pages/man7/unix.7.html)
- [Python socket](https://docs.python.org/3/library/socket.html)
- [Python select](https://docs.python.org/3/library/select.html)
- [Systemd services](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Python logging](https://docs.python.org/3/library/logging.html)

---

## 📊 Сравнение подходов

| Подход | Файл | Unix Socket | RPC |
|--------|------|-------------|-----|
| Race conditions | ❌ Есть | ✅ Нет | ✅ Нет |
| Запись на диск | ❌ Да | ✅ Нет | ✅ Нет |
| Push-модель | ❌ Polling | ✅ События | ✅ События |
| Скорость | 🐌 Медленно | ⚡ Быстро | ⚡ Быстро |
| Сложность | ✅ Просто | ✅ Средне | ❌ Сложно |

**Вывод:** Unix Domain Sockets — оптимальный баланс простоты и надёжности.

---

*Документ создан: 2026-03-30*
*Для реализации: см. план в разделе "План реализации"*

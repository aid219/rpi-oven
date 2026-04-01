# Настройка тачскрина FT6336U для Raspberry Pi

## Проблема
Стандартный overlay `ft6336u` не работает корректно — он не настраивает GPIO interrupt, поэтому драйвер не может привязаться к устройству.

## Решение
Создать кастомный device tree overlay с правильными параметрами interrupt.

---

## Пошаговая инструкция

### Шаг 1: Проверка оборудования

1. Подключитесь к Raspberry Pi по SSH:
```bash
ssh qummy@10.1.30.131
```

2. Проверьте, видно ли устройство на I2C шине:
```bash
sudo /usr/sbin/i2cdetect -y 1
```
Должно показать устройство на адресе `0x38`.

3. Проверьте доступные overlay:
```bash
ls /boot/firmware/overlays/ | grep ft
```

---

### Шаг 2: Установка необходимых пакетов

```bash
sudo apt-get update
sudo apt-get install -y device-tree-compiler i2c-tools evtest
```

---

### Шаг 3: Создание кастомного device tree overlay

1. Создайте файл `.dts`:
```bash
cat << 'EOF' > /tmp/ft6336u-fix.dts
/dts-v1/;
/plugin/;

/ {
    compatible = "brcm,bcm2837";

    fragment@0 {
        target = <&i2c1>;
        __overlay__ {
            #address-cells = <1>;
            #size-cells = <0>;
            status = "okay";

            ft6336u@38 {
                compatible = "focaltech,ft6236", "edt,edt-ft5x06";
                reg = <0x38>;
                interrupt-parent = <&gpio>;
                interrupts = <27 2>;
                touchscreen-size-x = <320>;
                touchscreen-size-y = <480>;
            };
        };
    };
};
EOF
```

**Важно:** 
- `interrupts = <27 2>` — GPIO 27 для interrupt (замените на свой GPIO если нужно)
- `touchscreen-size-x = <320>` и `touchscreen-size-y = <480>` — разрешение экрана
- `compatible = "focaltech,ft6236"` — драйвер лучше работает с этой совместимостью

2. Скомпилируйте overlay:
```bash
dtc -@ -I dts -O dtb -o /tmp/ft6336u-fix.dtbo /tmp/ft6336u-fix.dts
```

3. Скопируйте в директорию overlay:
```bash
sudo cp /tmp/ft6336u-fix.dtbo /boot/firmware/overlays/ft6336u-fix.dtbo
```

---

### Шаг 4: Настройка config.txt

1. Создайте резервную копию:
```bash
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.bak
```

2. Удалите старые настройки ft6336 (если есть):
```bash
sudo sed -i '/dtoverlay=ft6336u/d' /boot/firmware/config.txt
```

3. Добавьте новый overlay в конец файла:
```bash
echo "dtoverlay=ft6336u-fix" | sudo tee -a /boot/firmware/config.txt
```

4. Проверьте, что в config.txt есть:
```bash
dtparam=i2c_arm=on
dtoverlay=ft6336u-fix
```

---

### Шаг 5: Настройка автозагрузки модулей

Создайте файл для автозагрузки модулей ядра:
```bash
echo "regmap-i2c" | sudo tee /etc/modules-load.d/touchscreen.conf
echo "edt-ft5x06" | sudo tee -a /etc/modules-load.d/touchscreen.conf
```

---

### Шаг 6: Перезагрузка

```bash
sudo reboot
```

---

### Шаг 7: Проверка работы

После перезагрузки подключитесь и проверьте:

1. Проверьте input устройства:
```bash
ls -la /dev/input/
```
Должно появиться новое устройство `event5` (или другой номер).

2. Узнайте имя устройства:
```bash
for dev in event0 event1 event2 event3 event4 event5; do
    echo "=== /dev/input/$dev ==="
    cat /sys/class/input/$dev/device/name 2>/dev/null || cat /sys/class/input/$dev/name 2>/dev/null
done
```
Тачскрин должен отображаться как `1-0038 EP0110M09` или подобное.

3. Проверьте сообщения ядра:
```bash
dmesg | grep -i "ft5\|ft6\|touch\|edt"
```
Должно быть:
```
edt_ft5x06 1-0038: supply vcc not found, using dummy regulator
edt_ft5x06 1-0038: supply iovcc not found, using dummy regulator
```

4. Протестируйте касания:
```bash
sudo evtest /dev/input/event5
```
(замените `event5` на ваш номер устройства)

Теперь касайтесь экрана — должны выводиться события с координатами.

---

## Параметры для изменения

### Если используется другой GPIO для interrupt:
Измените в `.dts` файле:
```dts
interrupts = <27 2>;  # Замените 27 на ваш GPIO номер
```

### Если другое разрешение экрана:
Измените в `.dts`:
```dts
touchscreen-size-x = <800>;  # Ваша ширина
touchscreen-size-y = <480>;  # ваша высота
```

### Если тачскрин инвертирован:
Добавьте в `.dts`:
```dts
touchscreen-inverted-x;
touchscreen-inverted-y;
```

### Если нужно поменять X и Y местами:
Добавьте в `.dts`:
```dts
touchscreen-swapped-x-y;
```

---

## Решение проблем

### Проблема: Устройство не появляется в /dev/input/

**Проверка:**
```bash
# Проверьте I2C устройство
sudo /usr/sbin/i2cdetect -y 1

# Проверьте драйвер
lsmod | grep edt

# Проверьте привязку драйвера
cat /sys/bus/i2c/devices/1-0038/driver 2>/dev/null || echo "No driver bound"
```

**Решение:**
```bash
# Загрузите модули вручную
sudo insmod /lib/modules/$(uname -r)/kernel/drivers/base/regmap/regmap-i2c.ko.xz
sudo insmod /lib/modules/$(uname -r)/kernel/drivers/input/touchscreen/edt-ft5x06.ko.xz

# Привяжите драйвер вручную
echo "1-0038" | sudo tee /sys/bus/i2c/drivers/edt_ft5x06/bind
```

### Проблема: Ошибка "No such device" при привязке

Это означает, что драйвер не может прочитать устройство. Возможные причины:

1. **Неправильный GPIO interrupt** — проверьте подключение
2. **Устройство не отвечает** — проверьте питание и подключение I2C
3. **Неправильный compatible string** — попробуйте `focaltech,ft6236` вместо `focaltech,ft6336u`

### Проблема: Касания регистрируются, но координаты неверные

Откалибруйте тачскрин или добавьте в `.dts`:
```dts
touchscreen-inverted-x;  # Если X инвертирован
touchscreen-inverted-y;  # Если Y инвертирован
touchscreen-swapped-x-y; # Если X и Y поменяны местами
```

---

## Быстрая проверка работы

```bash
# Одной командой — проверить и протестировать
sudo evtest /dev/input/event5 2>&1 | head -20
```

Или создайте скрипт для проверки:
```bash
cat << 'EOF' > ~/test_touch.sh
#!/bin/bash
echo "Testing FT6336U touchscreen..."
echo "Devices:"
ls -la /dev/input/event*
echo ""
echo "Touch device name:"
cat /sys/class/input/event5/device/name 2>/dev/null
echo ""
echo "Run 'sudo evtest /dev/input/event5' to test touches"
EOF
chmod +x ~/test_touch.sh
```

---

## Итог

После настройки:
- Тачскрин доступен как `/dev/input/event5` (или другой номер)
- Поддерживается мультитач (до 2 касаний)
- Разрешение: 320x480 (или ваше)
- Автозагрузка при старте системы

**Устройство готово к использованию в ваших приложениях!**

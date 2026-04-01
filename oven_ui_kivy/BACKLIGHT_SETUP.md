# 🔆 Настройка плавной регулировки яркости

## Текущая проблема

**Сейчас:** `backlight_gpio` имеет только 2 состояния:
- **0** = выключено
- **1** = включено

**Причина:** GPIO backlight без PWM поддержки.

---

## ✅ Вариант 1: Текущий (вкл/выкл)

**Работает сейчас!** Слайдер в SETTINGS:
- **0-49%** → подсветка выключена
- **50-100%** → подсветка включена

---

## 🚀 Вариант 2: PWM регулировка (плавно)

### Шаг 1: Создать overlay

```bash
# На Raspberry Pi
sudo nano /boot/firmware/overlays/pwm-backlight-overlay.dts
```

**Содержимое:**
```dts
/dts-v1/;
/plugin/;

/ {
    compatible = "brcm,bcm2835";

    fragment@0 {
        target = <&backlight_gpio>;
        __overlay__ {
            compatible = "pwm-backlight";
            pwms = <&pwm 0 1000>;
            brightness-levels = <0 10 20 30 40 50 60 70 80 90 100 110 120 130 140 150
                                 160 170 180 190 200 210 220 230 240 255>;
            default-brightness-level = <20>;
        };
    };
};
```

### Шаг 2: Скомпилировать overlay

```bash
sudo dtc -I dts -O dtb -o /boot/firmware/overlays/pwm-backlight.dtbo /boot/firmware/overlays/pwm-backlight-overlay.dts
```

### Шаг 3: Добавить в config.txt

```bash
sudo nano /boot/firmware/config.txt
```

**Добавить:**
```ini
dtoverlay=pwm-backlight
```

### Шаг 4: Перезагрузка

```bash
sudo reboot
```

### Шаг 5: Проверить

```bash
ls /sys/class/backlight/
# Должно быть: pwm_backlight

cat /sys/class/backlight/pwm_backlight/max_brightness
# Должно быть: 255
```

---

## ⚡ Быстрая проверка GPIO 18

```bash
# Проверить текущую яркость
cat /sys/class/backlight/backlight_gpio/brightness

# Включить
echo 1 | sudo tee /sys/class/backlight/backlight_gpio/brightness

# Выключить
echo 0 | sudo tee /sys/class/backlight/backlight_gpio/brightness
```

---

## 📝 Примечания

1. **GPIO 18** = PWM0 (поддерживает плавную регулировку)
2. **Требуется device tree overlay** для pwm-backlight
3. **Без overlay** — только вкл/выкл

---

**Текущий статус:** ✅ ВКЛ/ВЫКЛ работает  
**PWM статус:** ❌ Требуется настройка overlay

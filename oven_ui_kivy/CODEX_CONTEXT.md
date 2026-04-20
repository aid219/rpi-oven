# Codex Project Context

Last updated: 2026-04-20

## Project

Kivy UI for Raspberry Pi Zero 2 W oven control.

Local workspace:

```text
/home/dmitrii/Documents/dev/yy/rpi-oven/oven_ui_kivy
```

Target Raspberry Pi project directory:

```text
/home/qummy/test/oven_ui_kivy
```

Do not treat `/home/qummy/rpi-oven/oven_ui_kivy` as the active target unless explicitly asked.

## Raspberry Pi Access

Host:

```text
10.1.30.131
```

User:

```text
qummy
```

Use SSH for target-machine checks and edits. Do not store the password in repository files.

Useful SSH pattern from this environment:

```bash
ssh -F /dev/null qummy@10.1.30.131
```

The local system SSH config may fail with:

```text
Bad owner or permissions on /etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf
```

Using `-F /dev/null` avoids that global config.

## Current Understanding

- The app is a Python/Kivy UI for a 320x480 display.
- The likely active entrypoint is `main_optimized.py`, not `main.py`.
- `main_optimized.py` builds a `ScreenManager` and registers:
  - `MainScreen`
  - `VideoScreen`
  - `DashboardScreen`
  - `SettingsScreen`
  - `MainWaitScreen`
- `encoder_handler.py` uses `pigpio` and initializes the rotary encoder in the background after UI startup.
- `MainWaitScreen` uses the custom font `fonts/MOSCOW2024.otf`, image assets, and encoder callbacks for timer changes.
- Video playback uses `assets/videos/1.mp4`.

## Known Mismatches

- `run.sh`, `README.md`, and `systemd/kivy-oven-ui.service` may still reference `main.py`.
- On the Raspberry Pi test directory, `systemd/kivy-oven-ui.service` was observed pointing to `/home/qummy/rpi-oven/oven_ui_kivy/main.py`, not the active test directory.
- Before configuring autostart for the test copy, update service paths to `/home/qummy/test/oven_ui_kivy/main_optimized.py`.

## Verification Already Done

Local syntax check passed:

```bash
python3 -m py_compile main_optimized.py encoder_handler.py screens/*.py
```

Main wait screen encoder/timer fix applied on 2026-04-20:

- `screens/main_wait_screen.py` now clamps timer changes at `00 00` instead of wrapping a negative step to `00 99`.
- Encoder dispatch deltas are normalized to one UI step per callback.
- Rotation direction was inverted on 2026-04-20 after hardware testing.
- Timer math now uses real seconds: `00:59 -> 01:00`, `01:00 -> 00:59`, lower clamp `00:00`, upper clamp `99:59`.
- Fast encoder rotation now preserves multi-step `delta` values instead of collapsing them to one step.
- Progressive acceleration was adjusted again: the first 60 continuous same-direction steps stay at 1x, then the multiplier grows by 1 every 20 more continuous steps. There is no fixed multiplier ceiling; the timer range clamp is the only upper bound. A direction change or pause over 0.35 s resets acceleration.
- Reverse-direction noise filtering was strengthened: while rotating continuously and accelerated, up to 31 opposite-direction callbacks are ignored and do not reset acceleration; 32 opposite callbacks in a row confirm an intentional direction change. Before acceleration, 2 opposite callbacks still confirm direction change.
- Timer digit labels were widened and spaced out to reduce glyph overlap with `MOSCOW2024.otf`.
- The same file was copied to `/home/qummy/test/oven_ui_kivy/screens/main_wait_screen.py`.
- Encoder timer behavior was extracted from `screens/main_wait_screen.py` into `encoder_timer_control.py`. Change timer range, acceleration, reverse-noise filtering, and direction behavior there instead of editing the Kivy screen.

Encoder handler update applied on 2026-04-20:

- `encoder_handler.py` now uses both encoder channels with a quadrature transition table.
- Invalid jumps reset the partial step accumulator.
- One UI step is emitted per full 4-transition detent.
- GPIO glitch filter was reduced from 20000 us to 1000 us.
- The same file was copied to `/home/qummy/test/oven_ui_kivy/encoder_handler.py`.
- Diagnostic scans on Raspberry Pi saw no GPIO changes on BCM 5/6, and then no changes on BCM 2-27 during the scan windows. If the encoder was physically rotated during those windows, check wiring, common ground, and whether the code should use different BCM pins.
- Do not scan or reconfigure broad GPIO ranges on this Raspberry Pi. The SPI display uses GPIO 7-11, backlight GPIO 18, reset GPIO 24, and DC GPIO 25. A broad GPIO scan on 2026-04-20 temporarily left those pins as inputs and caused a black screen. Recovery used `raspi-gpio set 7 a0`, `8 a0`, `9 a0`, `10 a0`, `11 a0`, `18 op dh`, `24 op dh`, `25 op dh`, then started `/home/qummy/test/oven_ui_kivy/main_optimized.py`.

Encoder button module added on 2026-04-20:

- Button wiring target pin: BCM GPIO17 (physical pin 11), second contact to GND.
- New module `encoder_button_handler.py` handles button input separately from rotary steps.
- Pull-up is internal (`PUD_UP`), press is active-low (`FALLING_EDGE`), debounce uses `set_glitch_filter(..., 50000)` (50 ms).
- `main_optimized.py` now initializes `EncoderButtonHandler(pin=17)` and injects it into screens that define `set_button_handler`.
- `screens/main_wait_screen.py` now registers button callbacks in `on_enter`/`on_leave`; button press acts as the main select action and calls `go_to_settings()`.

Door switch module added on 2026-04-20:

- Door switch wiring target pin: BCM GPIO23 (physical pin 16), second contact to GND.
- New module `door_switch_handler.py` handles door switch input separately from rotary encoder and button.
- Pull-up is internal (`PUD_UP`), active state is active-low, debounce uses `set_glitch_filter(..., 50000)` (50 ms).
- `main_optimized.py` now initializes `DoorSwitchHandler(pin=23)` and injects it into screens that define `set_door_switch_handler`.
- `screens/main_wait_screen.py` now registers door switch callbacks in `on_enter`/`on_leave` and stores state in `door_switch_active` for future door logic.

Raspberry Pi search found two copies:

```text
/home/qummy/rpi-oven/oven_ui_kivy
/home/qummy/test/oven_ui_kivy
```

The user selected:

```text
/home/qummy/test/oven_ui_kivy
```

## Working Rules

- Keep local and Raspberry Pi context synchronized when changing important project state.
- Prefer small, targeted changes.
- Do not write secrets, passwords, or private access tokens into project files.
- If resuming from a fresh session, read this file first.

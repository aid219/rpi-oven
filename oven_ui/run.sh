#!/bin/bash
sudo modprobe i2c-dev
sudo python3 /home/qummy/oven_ui/daemon/touch_daemon.py &
sleep 3
sudo python3 /home/qummy/oven_ui/ui/ui_debug.py

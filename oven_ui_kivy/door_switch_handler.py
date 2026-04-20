import threading
import logging
from kivy.clock import Clock

logger = logging.getLogger(__name__)


class DoorSwitchHandler:
    def __init__(self, pin=23, debounce_us=50000, active_low=True):
        self.pin = pin
        self.debounce_us = debounce_us
        self.active_low = active_low
        self.pi = None
        self.cb = None
        self._callbacks = []
        self._is_active = None

    def start(self, on_ready_callback=None):
        threading.Thread(target=self._init_pigpio, args=(on_ready_callback,), daemon=True).start()

    def _init_pigpio(self, on_ready_callback=None):
        try:
            import pigpio

            self.pi = pigpio.pi()
            if not self.pi.connected:
                raise RuntimeError("pigpiod not running. sudo pigpiod")

            self.pi.set_mode(self.pin, pigpio.INPUT)
            self.pi.set_pull_up_down(self.pin, pigpio.PUD_UP)
            self.pi.set_glitch_filter(self.pin, self.debounce_us)
            self._is_active = self._read_active()
            self.cb = self.pi.callback(self.pin, pigpio.EITHER_EDGE, self._irq)

            if on_ready_callback:
                Clock.schedule_once(lambda dt: on_ready_callback(True), 0)
        except Exception as e:
            logger.error(f"Door switch init failed: {e}")
            if on_ready_callback:
                Clock.schedule_once(lambda dt: on_ready_callback(False), 0)

    def _read_active(self):
        level = self.pi.read(self.pin)
        return (level == 0) if self.active_low else (level == 1)

    def _irq(self, gpio, level, tick):
        self._is_active = self._read_active()
        Clock.schedule_once(self._dispatch, 0)

    def _dispatch(self, dt):
        state = self._is_active
        for cb in self._callbacks:
            try:
                cb(state)
            except Exception as e:
                logger.error(f"Door switch callback error: {e}")

    def add_callback(self, callback):
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def remove_callback(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def is_active(self):
        return self._is_active

    def stop(self):
        if self.cb:
            self.cb.cancel()
        if self.pi:
            self.pi.stop()

import threading
import logging
from kivy.clock import Clock

logger = logging.getLogger(__name__)


class EncoderHandler:
    def __init__(self, clk_pin=5, dt_pin=6):
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.pi = None
        self.cb = None
        self._callbacks = []
        self._delta_acc = 0
        self._counter = 0
        self._pending = False
        self._lock = threading.Lock()

    def start(self, on_ready_callback=None):
        threading.Thread(target=self._init_pigpio, args=(on_ready_callback,), daemon=True).start()

    def _init_pigpio(self, on_ready_callback=None):
        try:
            import pigpio
            self.pi = pigpio.pi()
            if not self.pi.connected:
                raise RuntimeError("pigpiod не запущен. sudo pigpiod")

            self.pi.set_mode(self.clk_pin, pigpio.INPUT)
            self.pi.set_mode(self.dt_pin, pigpio.INPUT)
            self.pi.set_pull_up_down(self.clk_pin, pigpio.PUD_UP)
            self.pi.set_pull_up_down(self.dt_pin, pigpio.PUD_UP)
            self.pi.set_glitch_filter(self.clk_pin, 20000)
            self.pi.set_glitch_filter(self.dt_pin, 20000)
            self.cb = self.pi.callback(self.clk_pin, pigpio.EITHER_EDGE, self._irq)
            
            if on_ready_callback:
                Clock.schedule_once(lambda dt: on_ready_callback(True), 0)
        except Exception as e:
            logger.error(f"Encoder init failed: {e}")
            if on_ready_callback:
                Clock.schedule_once(lambda dt: on_ready_callback(False), 0)

    def _irq(self, gpio, level, tick):
        try:
            dt_level = self.pi.read(self.dt_pin)
            delta = 1 if level != dt_level else -1
            with self._lock:
                self._delta_acc += delta
                self._counter += delta
            if not self._pending:
                self._pending = True
                Clock.schedule_once(self._dispatch, 0)
        except Exception:
            pass

    def _dispatch(self, dt):
        self._pending = False
        with self._lock:
            delta = self._delta_acc
            value = self._counter
            self._delta_acc = 0
        if delta == 0:
            return
        for cb in self._callbacks:
            try:
                cb(value, delta)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def add_callback(self, callback):
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def remove_callback(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def reset(self):
        with self._lock:
            self._delta_acc = 0
            self._counter = 0

    def stop(self):
        if self.cb:
            self.cb.cancel()
        if self.pi:
            self.pi.stop()
import threading
import logging
from kivy.clock import Clock

logger = logging.getLogger(__name__)


class EncoderHandler:
    STEP_TRANSITIONS = 4
    _TRANSITIONS = {
        (0b00, 0b01): 1,
        (0b01, 0b11): 1,
        (0b11, 0b10): 1,
        (0b10, 0b00): 1,
        (0b00, 0b10): -1,
        (0b10, 0b11): -1,
        (0b11, 0b01): -1,
        (0b01, 0b00): -1,
    }

    def __init__(self, clk_pin=5, dt_pin=6):
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.pi = None
        self.cb_clk = None
        self.cb_dt = None
        self._callbacks = []
        self._delta_acc = 0
        self._counter = 0
        self._step_acc = 0
        self._last_state = None
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
            self.pi.set_glitch_filter(self.clk_pin, 1000)
            self.pi.set_glitch_filter(self.dt_pin, 1000)
            self._last_state = self._read_state()
            self.cb_clk = self.pi.callback(self.clk_pin, pigpio.EITHER_EDGE, self._irq)
            self.cb_dt = self.pi.callback(self.dt_pin, pigpio.EITHER_EDGE, self._irq)
            
            if on_ready_callback:
                Clock.schedule_once(lambda dt: on_ready_callback(True), 0)
        except Exception as e:
            logger.error(f"Encoder init failed: {e}")
            if on_ready_callback:
                Clock.schedule_once(lambda dt: on_ready_callback(False), 0)

    def _irq(self, gpio, level, tick):
        try:
            state = self._read_state()
            with self._lock:
                last_state = self._last_state
                self._last_state = state
                delta = self._TRANSITIONS.get((last_state, state), 0)
                if delta == 0:
                    self._step_acc = 0
                    return

                if self._step_acc and (self._step_acc > 0) != (delta > 0):
                    self._step_acc = 0
                self._step_acc += delta

                if abs(self._step_acc) < self.STEP_TRANSITIONS:
                    return

                step = 1 if self._step_acc > 0 else -1
                self._step_acc = 0
                self._delta_acc += step
                self._counter += step

            if not self._pending:
                self._pending = True
                Clock.schedule_once(self._dispatch, 0)
        except Exception:
            pass

    def _read_state(self):
        return (self.pi.read(self.clk_pin) << 1) | self.pi.read(self.dt_pin)

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
            self._step_acc = 0
            if self.pi:
                self._last_state = self._read_state()

    def stop(self):
        if self.cb_clk:
            self.cb_clk.cancel()
        if self.cb_dt:
            self.cb_dt.cancel()
        if self.pi:
            self.pi.stop()

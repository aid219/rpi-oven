import time


class EncoderTimerControl:
    MAX_TIMER_SECONDS = 99 * 60 + 59
    ACCEL_RESET_SECONDS = 0.35
    ACCEL_START_STEPS = 60
    ACCEL_STEPS_PER_MULTIPLIER = 20
    REVERSE_CONFIRM_STEPS = 2
    ACCEL_REVERSE_CONFIRM_STEPS = 32

    def __init__(self):
        self.reset_motion()

    def reset_motion(self):
        self._last_direction = 0
        self._last_time = 0
        self._run_steps = 0
        self._pending_reverse_direction = 0
        self._pending_reverse_steps = 0

    def apply_delta(self, minutes, seconds, delta):
        direction = -1 if delta > 0 else 1
        raw_steps = max(1, abs(delta))
        multiplier = self._get_multiplier(direction, raw_steps)
        if multiplier is None:
            return minutes, seconds

        step = direction * raw_steps * multiplier
        total = minutes * 60 + seconds
        total = max(0, min(self.MAX_TIMER_SECONDS, total + step))
        return divmod(total, 60)

    def _get_multiplier(self, direction, raw_steps):
        now = time.monotonic()
        same_run = (
            direction == self._last_direction and
            now - self._last_time <= self.ACCEL_RESET_SECONDS
        )

        if self._last_direction and not same_run and now - self._last_time <= self.ACCEL_RESET_SECONDS:
            confirm_steps = self._get_reverse_confirm_steps()
            if direction == self._pending_reverse_direction:
                self._pending_reverse_steps += raw_steps
            else:
                self._pending_reverse_direction = direction
                self._pending_reverse_steps = raw_steps

            if self._pending_reverse_steps < confirm_steps:
                self._last_time = now
                return None
        else:
            self._pending_reverse_direction = 0
            self._pending_reverse_steps = 0

        self._run_steps = self._run_steps + raw_steps if same_run else raw_steps
        self._last_direction = direction
        self._last_time = now
        self._pending_reverse_direction = 0
        self._pending_reverse_steps = 0

        if self._run_steps < self.ACCEL_START_STEPS:
            return 1

        accel_steps = self._run_steps - self.ACCEL_START_STEPS
        return 1 + accel_steps // self.ACCEL_STEPS_PER_MULTIPLIER

    def _get_reverse_confirm_steps(self):
        if self._run_steps >= self.ACCEL_START_STEPS:
            return self.ACCEL_REVERSE_CONFIRM_STEPS
        return self.REVERSE_CONFIRM_STEPS

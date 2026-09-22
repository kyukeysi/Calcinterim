import time


class GameTimer:
    def __init__(self, duration=60):
        self.duration = duration
        self.start_time = None
        self.running = False

    def start(self):
        self.start_time = time.monotonic()
        self.running = True

    def stop(self):
        self.running = False

    def reset(self):
        self.start_time = None
        self.running = False

    def get_elapsed(self):
        if self.start_time is None:
            return 0.0

        if not self.running:
            return min(
                self.duration,
                time.monotonic() - self.start_time
            )

        return time.monotonic() - self.start_time

    def get_remaining(self):
        remaining = self.duration - self.get_elapsed()
        return max(0.0, remaining)

    def is_expired(self):
        return self.get_remaining() <= 0.0

    def get_remaining_seconds(self):
        return int(self.get_remaining() + 0.999)

    def set_duration(self, duration):
        if duration < 0:
            raise ValueError("Timer duration cannot be negative.")

        self.duration = duration
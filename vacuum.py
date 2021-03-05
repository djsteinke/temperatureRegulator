import threading
import time
from relay import Relay
from settings import msg


class Vacuum(object):
    def __init__(self):
        self._start_time = None
        self._vacuum = Relay(24)
        self._started = False
        self._run_time = 3600

    def start(self):
        self._vacuum.on()
        msg["current"]["vacuum"] = self._vacuum.is_on()
        self._started = True
        self._start_time = time.perf_counter()

    def stop(self):
        self._vacuum.off()
        msg["current"]["vacuum"] = self._vacuum.is_on()
        self._started = False

    def wait(self):
        if time.perf_counter()-self._start_time > self._run_time:
            self.stop()
        else:
            timer = threading.Timer(5, self.wait)
            timer.start()

    def is_started(self):
        return self._started

    def is_on(self):
        return self._vacuum.is_on()

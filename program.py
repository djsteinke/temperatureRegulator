import threading
import time

from timer import Timer
from settings import msg


class ProgramError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Program(object):
    def __init__(self):
        self._start_time = None
        self._timer = Timer()
        self._started = False
        self._step = 0

    def is_running(self):
        return self._started

    def run(self):
        print("Program.run()")
        self._step = 1
        self._started = True
        self._start_time = time.perf_counter()
        msg['current']['step'] = self._step
        self.run_step()

    def run_step(self):
        found = False
        if self._started:
            for obj in msg['program']:
                if obj['step'] == self._step:
                    found = True
                    if not self._timer.is_running():
                        self._timer.start()
                        # TODO set temp
                    if self._timer.get_elapsed_time() / 60 > obj['time']:
                        self._step += 1
                        msg['current']['step'] = self._step
                        self._timer.stop()
                        break
        self._started = found
        if not self._started:
            print("program complete")
        else:
            self.wait()

    def wait(self):
        print(str(self._step) + " " + format(self._timer.get_elapsed_time(), '0.0f'))
        msg['current']['stepTime'] = int(self._timer.get_elapsed_time())
        msg['current']['elapsedTime'] = int(self.get_elapsed_time())
        timer = threading.Timer(6, self.run_step)
        timer.start()

    def stop(self):
        self._started = False

    def get_elapsed_time(self):
        if self._start_time is None:
            return 0
        else:
            return int(time.perf_counter() - self._start_time)

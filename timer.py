import logging
import time


module_logger = logging.getLogger("main.timer")


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Timer(object):
    def __init__(self):
        self._start_time = None
        self._running = False

    def start(self):
        module_logger.debug("start()")
        """Start a new timer"""
        if self._start_time is not None:
            module_logger.debug("Timer is running.")
            raise TimerError(f"Timer is running. Use .stop() to stop it")
        self._start_time = time.perf_counter()
        self._running = True

    def stop(self):
        module_logger.debug("stop()")
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            module_logger.debug("Timer is not running.")
            raise TimerError(f"Timer is not running. Use .start() to start it")
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        self._running = False
        module_logger.debug(f"Elapsed time: {elapsed_time:0.1f} seconds")
        print(f"Elapsed time: {elapsed_time:0.1f} seconds")

    def is_running(self):
        module_logger.debug("is_running()")
        return self._running

    def get_elapsed_time(self):
        t = 0
        if self._start_time is not None:
            t = time.perf_counter() - self._start_time
        module_logger.debug(f"get_elapsed_time({t:0.1f})")
        return t

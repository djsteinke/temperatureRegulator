import logging
import threading
import time

from timer import Timer
from settings import msg
from static import get_temperature
from relay import Relay

module_logger = logging.getLogger('main.program')
heat = Relay(23)


class ProgramError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Program(object):
    def __init__(self):
        self._start_time = None
        self._timer = Timer()
        self._started = False
        self._step = 0
        self._step_temp_reached = False

    def is_running(self):
        module_logger.debug("run_program(" + str(self._started) + ")")
        return self._started

    def run(self):
        module_logger.info("run() Program Started")
        print("Program.run()")
        self._step = 1
        self._started = True
        self._start_time = time.perf_counter()

        msg["current"]["step"] = self._step
        msg["current"]["started"] = self._started
        self.run_step()

    def run_step(self):
        module_logger.debug(f"run_step({self._step})")
        found = False
        if self._started:
            for obj in msg["program"]:
                if obj["step"] == self._step:
                    found = True
                    if not self._timer.is_running():
                        module_logger.debug("_timer.start()")
                        msg["current"]["step"] = self._step
                        msg["current"]["stepTemperature"] = obj["temperature"]
                        if msg["current"]["temperature"] > msg["current"]["stepTemperature"]:
                            self._timer.start()

                    if msg["current"]["temperature"] > msg["current"]["stepTemperature"]:
                        heat.off()
                    else:
                        heat.on()
                    msg["current"]["heat"] = heat.is_on()

                    if self._timer.get_elapsed_time() / 60 > obj["time"]:
                        self._step += 1
                        module_logger.debug(f"_step({self._step})")
                        msg["current"]["step"] = self._step
                        self._step_temp_reached = False
                        self._timer.stop()
                        break
        self._started = found
        if not self._started:
            module_logger.info("Program Complete")
            msg["current"]["started"] = self._started
            heat.off()
            print("program complete")
        else:
            self.wait()

    def wait(self):
        print(f"_step[{self._step}] _timer[{self._timer.get_elapsed_time():0.1f}]")
        msg["current"]["stepTime"] = int(self._timer.get_elapsed_time())
        msg["current"]["elapsedTime"] = int(self.get_elapsed_time())
        get_temperature()
        timer = threading.Timer(5, self.run_step)
        timer.start()

    def stop(self):
        module_logger.debug("stop()")
        self._started = False

    def get_elapsed_time(self):
        if self._start_time is None:
            return 0
        else:
            return int(time.perf_counter() - self._start_time)

import logging
import threading
import time

from static import get_temp
from relay import Relay
from properties import heat_pin, vacuum_pin
from status import Status
from history import History

module_logger = logging.getLogger('main.hot_box')


class HotBox(object):
    def __init__(self):
        self._hold_timer = None
        self._step_timer = None
        self._heat_timer = None
        self._status = Status()
        self._history = []
        self._p_start_time = None
        self._s_start_time = None
        self._r_start_time = None
        self._heat = Relay(heat_pin)
        self._vacuum = Relay(vacuum_pin)
        self._callback = None
        self._program = None
        self._recording = False

    def heat_on(self, temp, run_time):
        self._s_start_time = time.perf_counter()
        self._status.hold_temperature = temp
        if run_time is None:
            run_time = 3600
        self._status.step_time = run_time
        self._heat.on()
        self._status.heat_running = True
        self._status.heat_on = self._heat.is_on
        self.hold_temp()
        self._heat_timer = threading.Timer(run_time, self.heat_off)
        self._heat_timer.start()
        if not self._recording:
            self.record()

    def heat_cancel(self):
        self._heat.force_off()
        self.heat_off()

    def heat_off(self):
        self._heat.run_time = 0
        self._status.step_time = 0
        self._status.hold_temperature = 0
        self._status.elapsed_step_time = 0
        self._status.heat_running = False
        self._status.heat_on = self._heat.is_on
        if self._heat_timer is not None:
            self._heat_timer.cancel()
        if self._hold_timer is not None:
            self._hold_timer.cancel()

    def vacuum_on(self, run_time):
        if run_time is None:
            run_time = 3600
        self._vacuum.run_time = run_time
        self._callback = self.vacuum_off
        self._vacuum.on()
        self._status.vacuum_running = self._vacuum.is_on
        if not self._recording:
            self.record()

    def vacuum_cancel(self):
        self._vacuum.force_off()
        self.vacuum_off()

    def vacuum_off(self):
        self._vacuum.run_time = 0
        self._status.vacuum_time_remaining = 0
        self._status.vacuum_running = self._vacuum.is_on

    def end_program(self):
        self._status.step = -1
        self._status.hold_temperature = 0
        self._status.prog_running = False
        if self._hold_timer is not None:
            self._hold_timer.cancel()
            self._hold_timer = None
        if self._step_timer is not None:
            self._step_timer.cancel()
            self._step_timer = None
        if self._heat.is_on:
            self._heat.force_off()
        if self._vacuum.is_on:
            self._vacuum.force_off()
        self._status.heat_running = self._heat.is_on
        self._status.vacuum_running = self._vacuum.is_on
        module_logger.info(f"Program Ended")
        if self._callback is not None:
            self._callback()

    def start_program(self, name):
        print("Program.run()")
        self._p_start_time = time.perf_counter()
        self._status.prog_running = True
        self.run_step()
        if not self._recording:
            self.record()
        module_logger.info(f"Program {name} Started")

    def run_step(self):
        self._status.step += 1
        self._s_start_time = None
        if not self._status.prog_running or self._status.step >= len(self._program):
            self.end_program()
        else:
            found = False
            for obj in self._program:
                if obj["step"] == self._status.step:
                    found = True
                    self._s_start_time = time.perf_counter()
                    self._status.set_temperature = obj["temperature"]
                    if self._hold_timer is not None:
                        self.hold_temp()
                    t = obj['time']*60
                    self._step_timer = threading.Timer(t, self.run_step)
                    self._step_timer.start()
            self._status.prog_running = found
            if not self._status.prog_running:
                self.end_program()

    def hold_temp(self):
        t = get_temp()
        self._status.temperature = t[0]
        self._status.humidity = t[1]
        self._status.elapsed_step_time = self.time_in_step()
        self._status.elapsed_program_time = self.time_in_program()
        if self._vacuum.is_on:
            self._status.vacuum_time_remaining = self._vacuum.run_time-self._vacuum.on_time()
        if self._status.hold_temperature > 0:
            if self._status.temperature > self._status.hold_temperature:
                self._heat.force_off()
            else:
                self._heat.on()
        self._status.heat_on = self._heat.is_on
        self._hold_timer = threading.Timer(10, self.hold_temp)
        self._hold_timer.start()

    def time_in_step(self):
        if self._s_start_time is None:
            return 0
        else:
            return int(time.perf_counter() - self._s_start_time)

    def time_in_program(self):
        if self._p_start_time is None:
            return 0
        else:
            return int(time.perf_counter() - self._p_start_time)

    def record(self):
        if not self._recording:
            self._r_start_time = time.perf_counter()
        if self._status.heat_running or self._status.vacuum_running or self._status.prog_running:
            self._recording = True
            history = History()
            history.vacuum = self._status.vacuum_running
            if not (self._status.heat_running or self._status.prog_running):
                r = get_temp()
                history.temp = r[0]
                self._status.temperature = r[0]
            else:
                history.temp = self._status.temperature
            history.time = int(time.perf_counter() - self._r_start_time)
            history.set_temp = self._status.hold_temperature
            self._status.recording_time = history.time
            self._status.add_history(history)
            timer = threading.Timer(10, self.record)
            timer.start()
        else:
            self._recording = False
            self._status.history.clear()

    @property
    def status(self):
        if not (self._status.prog_running or self._status.heat_running or
                self._status.vacuum_running):
            r = get_temp()
            self._status.temperature = r[0]
            self._status.humidity = r[1]
        return self._status

    @property
    def callback(self):
        return self._callback

    @property
    def program(self):
        return self._program

    @callback.setter
    def callback(self, value):
        self._callback = value

    @program.setter
    def program(self, value):
        self._program = value

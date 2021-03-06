import logging
import threading
import time
import json

from ComplexEncoder import ComplexEncoder
from static import get_temp
from relay import Relay
from properties import heat_pin, vacuum_pin
from status import Status
from history import History
from settings import Settings
from define.program import Program

module_logger = logging.getLogger('main.hot_box')
max_temp_c = 72


class HotBox(object):
    def __init__(self):
        self._settings = Settings()
        self._status = Status()
        self._program = Program()
        self._hold_timer = None
        self._step_timer = None
        self._heat_timer = None
        self._record_timer = None
        self._history = []
        self._p_start_time = 0.0
        self._s_start_time = 0.0
        self._r_start_time = 0.0
        self._heat = Relay(heat_pin)
        self._vacuum = Relay(vacuum_pin)
        self._callback = None
        self._recording = False

    def repr_json(self):
        return dict(programStartTime=self.p_start_time,
                    stepStartTime=self.s_start_time,
                    recordStartTime=self.r_start_time,
                    status=self.status,
                    program=self.program)

    def heat_on(self, temp, run_time):
        self.s_start_time = time.perf_counter()
        self.status.hold_temperature = temp
        if run_time is None:
            run_time = 3600
        self.status.step_time = run_time
        self.heat.on()
        self.status.heat_running = True
        self.status.heat_on = self.heat.is_on
        self.hold_step()
        self.heat_timer = threading.Timer(run_time, self.heat_off)
        self.heat_timer.start()
        if not self.recording:
            self.record()

    def heat_cancel(self):
        self.heat.force_off()
        self.heat_off()

    def heat_off(self):
        self.heat.run_time = 0
        self.s_start_time = 0
        self.status.step_time = 0
        self.status.hold_temperature = 0
        self.status.elapsed_step_time = 0
        self.status.heat_running = False
        self.status.heat_on = self.heat.is_on
        if self.heat_timer is not None:
            self.heat_timer.cancel()
            self.heat_timer = None
        if self.hold_timer is not None:
            self.hold_timer.cancel()
            self.hold_timer = None

    def vacuum_on(self, run_time):
        if run_time is None:
            run_time = 3600
        self.vacuum.run_time = run_time
        self.vacuum.callback = self.vacuum_off
        self.vacuum.on()
        self.status.vacuum_running = True
        if not self.recording:
            self.record()

    def vacuum_cancel(self):
        module_logger.debug("vacuum_cancel()")
        self.vacuum.force_off()

    def vacuum_off(self):
        module_logger.debug("vacuum_off()")
        self.vacuum.run_time = 0
        self.status.vacuum_time_remaining = 0
        self.status.vacuum_running = self.vacuum.is_on

    def start_program(self, name):
        module_logger.info(f"Program.run({name})")
        found = False
        for p in self.settings.programs:
            print(p.name)
            if p.name == name:
                self.program = p
                found = True
                break
        if found:
            self.p_start_time = time.perf_counter()
            self.status.prog_running = True
            self.hold_timer = None
            self.run_step()
            if not self.recording:
                self.record()
            module_logger.info(f"Program {name} Started")
            return [200, f"Program {name} Started"]
        else:
            module_logger.error(f"Program {name} Not Found")
            return [400, f"Program {name} Not Found"]

    def end_program(self):
        self.status.step = -1
        self.status.hold_temperature = 0
        self.status.elapsed_program_time = 0
        self.p_start_time = 0
        self.status.prog_running = False
        if self.hold_timer is not None:
            self.hold_timer.cancel()
            self.hold_timer = None
        if self.step_timer is not None:
            self.step_timer.cancel()
            self.step_timer = None
        self.heat.force_off()
        self.vacuum.force_off()
        self.status.heat_running = self.heat.is_on
        self.status.vacuum_running = self.vacuum.is_on
        module_logger.info(f"Program Ended")
        if self.callback is not None:
            self.callback()

    def run_step(self):
        self.status.step += 1
        self.s_start_time = None
        if self.status.prog_running and self.status.step < len(self.program.steps):
            found = False
            for obj in self.program.steps:
                if obj.step == self.status.step:
                    found = True
                    self.s_start_time = time.perf_counter()
                    self.status.hold_temperature = float(obj.temperature)
                    t = obj.time*60
                    self.status.step_time = t
                    self.step_timer = threading.Timer(t, self.run_step)
                    self.step_timer.start()
                    if self.hold_timer is None:
                        self.hold_step()
                    if obj.vacuum:
                        self.vacuum.run_time = t
                        self.vacuum.on()
            self.status.prog_running = found
            module_logger.debug(json.dumps(self.repr_json(), cls=ComplexEncoder))
            if not self.status.prog_running:
                self.end_program()
        else:
            self.end_program()

    def hold_step(self):
        t = get_temp()
        self.status.temperature = t[0]
        self.status.humidity = t[1]
        self.status.elapsed_step_time = self.time_in_step()
        self.status.elapsed_program_time = self.time_in_program()
        if self.vacuum.is_on:
            self.status.vacuum_time_remaining = self.vacuum.run_time-self.vacuum.on_time()
        if self.status.hold_temperature > 0:
            if self.status.temperature <= self.status.hold_temperature and self.status.temperature < max_temp_c:
                if not self.heat.is_on:
                    self.heat.on()
            else:
                self.heat.force_off()
        self.status.heat_on = self._heat.is_on
        self.hold_timer = threading.Timer(15, self.hold_step)
        self.hold_timer.start()

    def time_in_step(self):
        if self.s_start_time > 0:
            return int(time.perf_counter() - self.s_start_time)
        else:
            return 0

    def time_in_program(self):
        if self.p_start_time > 0:
            return int(time.perf_counter() - self.p_start_time)
        else:
            return 0

    def record(self):
        self.recording = True
        if not self.recording:
            self.status.history.clear()
            self.r_start_time = time.perf_counter()
        history = History()
        status = self.status
        history.vacuum = status.vacuum_running
        history.temp = status.temperature
        history.time = int(time.perf_counter() - self.r_start_time)
        history.set_temp = status.hold_temperature
        status.recording_time = history.time
        status.add_history(history)
        self.status = status
        self.record_timer = threading.Timer(15, self.record)
        self.record_timer.start()

    def stop_record(self):
        if self.record_timer is not None:
            self.record_timer.cancel()
            self.record_timer = None
        self.recording = True

    @property
    def record_timer(self):
        return self._record_timer

    @property
    def hold_timer(self):
        return self._hold_timer

    @property
    def step_timer(self):
        return self._step_timer

    @property
    def heat_timer(self):
        return self._heat_timer

    @property
    def history(self):
        return self._history

    @property
    def p_start_time(self):
        return self._p_start_time

    @property
    def s_start_time(self):
        return self._s_start_time

    @property
    def r_start_time(self):
        return self._r_start_time

    @property
    def heat(self):
        return self._heat

    @property
    def vacuum(self):
        return self._vacuum

    @property
    def recording(self):
        return self._recording

    @property
    def program(self):
        return self._program

    @property
    def settings(self):
        return self._settings

    @property
    def status(self):
        if self.hold_timer is None:
            r = get_temp()
            self._status.temperature = r[0]
            self._status.humidity = r[1]
        return self._status

    @property
    def callback(self):
        return self._callback

    @record_timer.setter
    def record_timer(self, record_timer):
        self._record_timer = record_timer

    @hold_timer.setter
    def hold_timer(self, hold_timer):
        self._hold_timer = hold_timer

    @step_timer.setter
    def step_timer(self, step_timer):
        self._step_timer = step_timer

    @heat_timer.setter
    def heat_timer(self, heat_timer):
        self._heat_timer = heat_timer

    @history.setter
    def history(self, history):
        self._history = history

    @p_start_time.setter
    def p_start_time(self, p_start_time):
        self._p_start_time = p_start_time

    @s_start_time.setter
    def s_start_time(self, s_start_time):
        self._s_start_time = s_start_time

    @r_start_time.setter
    def r_start_time(self, r_start_time):
        self._r_start_time = r_start_time

    @heat.setter
    def heat(self, heat):
        self._heat = heat

    @vacuum.setter
    def vacuum(self, vacuum):
        self._vacuum = vacuum

    @recording.setter
    def recording(self, recording):
        self._recording = recording

    @program.setter
    def program(self, program):
        self._program = program

    @settings.setter
    def settings(self, settings):
        self._settings = settings

    @status.setter
    def status(self, status):
        self._status = status

    @callback.setter
    def callback(self, callback):
        self._callback = callback

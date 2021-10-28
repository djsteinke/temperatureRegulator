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

module_logger = logging.getLogger('main.hotbox')
max_temp_c = 72
interval = 15


class Hotbox(object):
    def __init__(self):
        self._settings = Settings()
        self._status = Status()
        self._program = Program()
        self._hold_timer = None
        self._step_timer = None
        self._heat_timer = None
        self._record_timer = None
        self._history = []
        self._lamp_on_time = 0
        self._lamp_on_temp = 0
        self._program_start_time = 0.0
        self._step_start_time = 0.0
        self._record_start_time = 0.0
        self._heat = Relay(heat_pin)
        self._vacuum = Relay(vacuum_pin)
        self._callback = None
        self._recording = False

    def start(self):
        if not self.recording:
            self.record()

    def repr_json(self):
        return dict(programStartTime=self.program_start_time,
                    stepStartTime=self.step_start_time,
                    recordStartTime=self.record_start_time,
                    status=self.status,
                    program=self.program)

    def start_heat(self, temp, run_time):
        self.step_start_time = time.perf_counter()
        if run_time is None or run_time == 0:
            run_time = 1800
        self.status.hold_temperature = temp
        self.status.step_time = run_time
        self.hold_step()
        self.status.heat_running = True
        self.status.heat_on = self.heat.is_on
        if self.heat_timer is not None:
            self.heat_timer.cancel()
            self.heat_timer = None
        self.heat_timer = threading.Timer(run_time, self.stop_heat)
        self.heat_timer.start()

    def stop_heat(self):
        self.heat.force_off()
        self.step_start_time = 0
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

    def start_vacuum(self, run_time):
        module_logger.debug(f'start_vacuum({str(run_time)})')
        if run_time is None:
            run_time = 1800
        self.vacuum.run_time = run_time
        self.vacuum.callback = self.stop_vacuum
        self.vacuum.on()
        self.status.vacuum_on = True
        self.status.vacuum_time_remaining = run_time
        if not self.recording:
            self.record()

    def stop_vacuum(self):
        module_logger.debug("stop_vacuum()")
        self.vacuum.force_off()
        self.status.vacuum_time_remaining = 0
        self.status.vacuum_on = self.vacuum.is_on

    def start_program(self, name):
        module_logger.info(f"Program.run({name})")
        self.status.running = "program"
        found = False
        for p in self.settings.programs:
            print(p.name)
            if p.name == name:
                self.program = p
                found = True
                break
        if found:
            self.program_start_time = time.perf_counter()
            self.status.program_running = True
            self.status.running = name
            self.hold_timer = None
            threading.Timer(1, self.run_step).start()
            if not self.recording:
                self.record()
            module_logger.info(f"Program {name} Started")
            return [200, f"Program {name} Started"]
        else:
            module_logger.error(f"Program {name} Not Found")
            return [400, f"Program {name} Not Found"]

    def run_step(self):
        self.status.step += 1
        self.step_start_time = None
        self.status.vacuum_running = False
        if self.status.program_running and self.status.step < len(self.program.steps):
            found = False
            for obj in self.program.steps:
                if obj.step == self.status.step:
                    found = True
                    self.step_start_time = time.perf_counter()
                    t = obj.time*60
                    self.start_heat(float(obj.temperature), t)
                    self.step_timer = threading.Timer(t, self.run_step)
                    self.step_timer.start()
                    if obj.vacuum:
                        self.vacuum.run_time = t
                        if not self.vacuum.is_on:
                            self.vacuum.on()
                        self.status.vacuum_running = True
                        self.status.vacuum_on = True
            self.status.program_running = found
            module_logger.debug(json.dumps(self.repr_json(), cls=ComplexEncoder))
            if not self.status.program_running:
                self.end_program()
        else:
            self.end_program()

    def end_program(self):
        self.status.running = None
        self.status.step = -1
        self.status.hold_temperature = 0
        self.status.elapsed_program_time = 0
        self.program_start_time = 0
        self.status.program_running = False
        self.status.running = None
        if self.hold_timer is not None:
            self.hold_timer.cancel()
            self.hold_timer = None
        if self.step_timer is not None:
            self.step_timer.cancel()
            self.step_timer = None
        self.heat.force_off()
        self.vacuum.force_off()
        self.status.heat_on = self.heat.is_on
        self.status.vacuum_on = self.vacuum.is_on
        module_logger.info(f"Program Ended")
        if self.callback is not None:
            self.callback()

    def hold_step(self):
        t = get_temp()
        if self.heat.is_on:
            if self._lamp_on_temp == 0:
                self._lamp_on_temp = t[0]
            self._lamp_on_time = self._lamp_on_time + interval
        else:
            self._lamp_on_time = 0
            self._lamp_on_temp = 0
        if self._lamp_on_time >= 300 and t[0] <= self._lamp_on_temp + 5:
            temp_change = t[0] - self._lamp_on_temp
            module_logger.error(f'EMERGENCY STOP PROGRAM. 5 min temp change {temp_change} deg C.')
            self.end_program()
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
        self.hold_timer = threading.Timer(interval, self.hold_step)
        self.hold_timer.start()

    def time_in_step(self):
        if self.step_start_time > 0:
            return int(time.perf_counter() - self.step_start_time)
        else:
            return 0

    def time_in_program(self):
        if self.program_start_time > 0:
            return int(time.perf_counter() - self.program_start_time)
        else:
            return 0

    def record(self):
        self.recording = True
        if not self.recording:
            self.status.history.clear()
            self.record_start_time = time.perf_counter()
        history = History()
        status = self.status
        history.heat = self.heat.is_on
        history.vacuum = self.vacuum.is_on
        history.temp = status.temperature
        history.time = int(time.perf_counter() - self.record_start_time)
        history.target_temp = status.hold_temperature
        status.recording_time = history.time
        status.add_history(history)
        self.status = status
        self.record_timer = threading.Timer(interval, self.record)
        self.record_timer.start()

    def stop_record(self):
        self.recording = False
        if self.record_timer is not None:
            self.record_timer.cancel()
            self.record_timer = None

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
    def program_start_time(self):
        return self._program_start_time

    @property
    def step_start_time(self):
        return self._step_start_time

    @property
    def record_start_time(self):
        return self._record_start_time

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

    @program_start_time.setter
    def program_start_time(self, program_start_time):
        self._program_start_time = program_start_time

    @step_start_time.setter
    def step_start_time(self, step_start_time):
        self._step_start_time = step_start_time

    @record_start_time.setter
    def record_start_time(self, record_start_time):
        self._record_start_time = record_start_time

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

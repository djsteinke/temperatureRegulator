
class Status(object):
    def __init__(self):
        self._humidity = 0.0
        self._temperature = 0.0
        self._hold_temperature = 0.0
        self._step = -1
        self._step_time = 0
        self._elapsed_program_time = 0
        self._elapsed_step_time = 0
        self._heat_running = False
        self._heat_on = False
        self._vacuum_running = False
        self._running = False
        self._vacuum_time_remaining = 0
        self._recording_time = 0
        self._history = []

    def repr_json(self):
        return dict(humidity=self.humidity,
                    temperature=self.temperature,
                    holdTemperature=self.hold_temperature,
                    step=self.step,
                    stepTime=self.step_time,
                    elapsedProgramTime=self.elapsed_program_time,
                    elapsedStepTime=self.elapsed_step_time,
                    heatRunning=self.heat_running,
                    heatOn=self.heat_on,
                    vacuumRunning=self.vacuum_running,
                    programRunning=self.prog_running,
                    vacuumTimeRemaining=self.vacuum_time_remaining,
                    recordingTime=self.recording_time,
                    history=self.history)

    def add_history(self, val):
        cnt = 60*4
        h_l = len(self.history)
        while h_l >= cnt:
            self.history.pop(0)
        self.history.append(val)

    @property
    def recording_time(self):
        return self._recording_time

    @property
    def history(self):
        return self._history

    @property
    def humidity(self):
        return self._humidity

    @property
    def temperature(self):
        return self._temperature

    @property
    def hold_temperature(self):
        return self._hold_temperature

    @property
    def step(self):
        return self._step

    @property
    def step_time(self):
        return self._step_time

    @property
    def elapsed_program_time(self):
        return self._elapsed_program_time

    @property
    def elapsed_step_time(self):
        return self._elapsed_step_time

    @property
    def heat_running(self):
        return self._heat_running

    @property
    def heat_on(self):
        return self._heat_on

    @property
    def vacuum_running(self):
        return self._vacuum_running

    @property
    def vacuum_time_remaining(self):
        return self._vacuum_time_remaining

    @property
    def prog_running(self):
        return self._running

    @recording_time.setter
    def recording_time(self, value):
        self._recording_time = value

    @humidity.setter
    def humidity(self, value):
        self._humidity = value

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

    @hold_temperature.setter
    def hold_temperature(self, value):
        self._hold_temperature = value

    @step.setter
    def step(self, value):
        self._step = value

    @step_time.setter
    def step_time(self, value):
        self._step_time = value

    @elapsed_program_time.setter
    def elapsed_program_time(self, value):
        self._elapsed_program_time = value

    @elapsed_step_time.setter
    def elapsed_step_time(self, value):
        self._elapsed_step_time = value

    @heat_running.setter
    def heat_running(self, value):
        self._heat_running = value

    @heat_on.setter
    def heat_on(self, value):
        self._heat_on = value

    @vacuum_running.setter
    def vacuum_running(self, value):
        self._vacuum_running = value

    @vacuum_time_remaining.setter
    def vacuum_time_remaining(self, value):
        self._vacuum_time_remaining = value

    @prog_running.setter
    def prog_running(self, value):
        self._running = value

    @history.setter
    def history(self, value):
        self._history = value

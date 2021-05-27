
class Status(object):
    def __init__(self):
        self._humidity = 0.0
        self._temperature = 0.0
        self._hold_temperature = 0.0
        self._step = -1
        self._step_time = 0
        self._elapsed_program_time = 0
        self._elapsed_step_time = 0
        self._heat_on = False
        self._vacuum_on = False
        self._running = False
        self._vacuum_time_remaining = 0
        self._history = []

    def repr_json(self):
        return dict(humidity=self.humidity,
                    temperature=self.temperature,
                    holdTemperature=self.hold_temperature,
                    step=self.step,
                    stepTime=self.step_time,
                    elapsedProgramTime=self._elapsed_program_time,
                    elapsedStepTime=self.elapsed_step_time,
                    heatOn=self.heat,
                    vacuumOn=self.vacuum,
                    running=self.running,
                    vacuumTimeRemaining=self.vacuum_time_remaining,
                    history=self.history)

    def add_history(self, val):
        self._history.append(val)

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
    def heat(self):
        return self._heat_on

    @property
    def vacuum(self):
        return self._vacuum_on

    @property
    def vacuum_time_remaining(self):
        return self._vacuum_time_remaining

    @property
    def running(self):
        return self._running

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

    @heat.setter
    def heat(self, value):
        self._heat_on = value

    @vacuum.setter
    def vacuum(self, value):
        self._vacuum_on = value

    @vacuum_time_remaining.setter
    def vacuum_time_remaining(self, value):
        self._vacuum_time_remaining = value

    @running.setter
    def running(self, value):
        self._running = value

    @history.setter
    def history(self, value):
        self._history = value
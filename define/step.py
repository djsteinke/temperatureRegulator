
class Step(object):
    def __init__(self, **kwargs):
        self._step = kwargs.get('step', 0)
        self._temperature = kwargs.get('temperature', 0)
        self._time = kwargs.get('time', 0)
        self._rate = kwargs.get('rate', 0)
        self._vacuum = kwargs.get('vacuum', False)

    def repr_json(self):
        return dict(step=self.step,
                    temperature=self.temperature,
                    time=self.time,
                    rate=self.rate,
                    vacuum=self.vacuum)

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        self._step = value

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, value):
        self._rate = value

    @property
    def vacuum(self):
        return self._vacuum

    @vacuum.setter
    def vacuum(self, value):
        self._vacuum = value


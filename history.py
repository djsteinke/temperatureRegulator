
class History(object):
    def __init__(self):
        self._time = 0
        self._temp = 0
        self._target_temp = 0
        self._vacuum = False
        self._heat = False

    def repr_json(self):
        return dict(time=self.time, temp=self.temp, setTemp=self.target_temp, vacuum=self.vacuum, heat=self.heat)

    @property
    def time(self):
        return self._time

    @property
    def temp(self):
        return self._temp

    @property
    def target_temp(self):
        return self._target_temp

    @property
    def vacuum(self):
        return self._vacuum

    @property
    def heat(self):
        return self._heat

    @time.setter
    def time(self, value):
        self._time = value

    @temp.setter
    def temp(self, value):
        self._temp = value

    @vacuum.setter
    def vacuum(self, value):
        self._vacuum = value

    @target_temp.setter
    def target_temp(self, value):
        self._target_temp = value

    @heat.setter
    def heat(self, value):
        self._heat = value

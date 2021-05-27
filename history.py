
class History(object):
    def __init__(self):
        self._time = 0
        self._temp = 0
        self._vacuum = False

    @property
    def time(self):
        return self._time

    @property
    def temp(self):
        return self._temp

    @property
    def vacuum(self):
        return self._vacuum

    @time.setter
    def time(self, value):
        self._time = value

    @temp.setter
    def temp(self, value):
        self._temp = value

    @vacuum.setter
    def vacuum(self, value):
        self._vacuum = value

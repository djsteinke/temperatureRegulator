from define.step import Step


class Program(object):
    def __init__(self, **kwargs):
        self._name = kwargs.get('name', "")
        self._steps = kwargs.get('steps', [])

    def repr_json(self):
        return dict(name=self.name,
                    steps=self.steps)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def steps(self):
        return self._steps

    @steps.setter
    def steps(self, value):
        self._steps = value

    def add_step(self, step):
        self._steps.append(step)

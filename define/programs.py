from typing import List

from define.program import Program


class Programs(object):
    def __init__(self, **kwargs):
        self._programs = kwargs.get('programs', [])

    def repr_json(self):
        return dict(programs=self.programs)

    @property
    def programs(self):
        return self._programs

    @programs.setter
    def programs(self, value):
        self._programs = value




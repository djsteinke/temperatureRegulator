import json
import logging

from ComplexEncoder import ComplexEncoder
from define.program import Program
from define.programs import Programs
from define.step import Step

module_logger = logging.getLogger('main.settings')


def load(file):
    try:
        f = open(file, "r")
        contents = f.read()
        f.close()
        return contents
    except FileNotFoundError:
        return None


def save(file, value):
    f = open(file, "w")
    f.write(value)
    f.close()


class Settings(object):
    def __init__(self):
        self._file = "programs.json"
        self._msg = 1
        self._programs = Programs()

    @property
    def file(self):
        return self._file

    @property
    def programs(self):
        return self._programs.programs

    def load(self):
        c = load(self.file)
        if c is not None:
            j = json.loads(c)
            self.process_programs_json(j)

    def update_program(self, p):
        module_logger.debug(json.dumps(p))
        found = False
        i = 0
        program = Program(**p)
        program.steps = []
        for item_s in p['steps']:
            step = Step(**item_s)
            program.steps.append(step)

        for item in self.programs:
            if item.name == program.name:
                self.programs[i] = p
                found = True
                break
            i += 1
        if not found:
            self.programs.append(p)
        s_str = json.dumps(self._programs.repr_json(), cls=ComplexEncoder)
        print(s_str)
        save(self.file, s_str)

    def process_programs_json(self, j):
        self._programs = Programs()
        for item_p in j['programs']:
            program = Program(**item_p)
            program.steps = []
            for item_s in item_p['steps']:
                step = Step(**item_s)
                program.steps.append(step)
            self.programs.append(program)
        print(type(self._programs))
        print(json.dumps(self._programs.repr_json(), cls=ComplexEncoder))

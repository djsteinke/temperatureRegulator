import json

from ComplexEncoder import ComplexEncoder
from define.program import Program
from define.programs import Programs
from define.step import Step

msg = {
    "vacuum": {
        "time": 3600
    },
    "program": [
        {
            "step": 1,
            "temperature": 25,
            "time": 1,
            "rate": 0,
            "vacuum": 60,
        },
        {
            "step": 3,
            "temperature": 0,
            "time": 1,
            "rate": 0,
            "vacuum": 0,
        },
        {
            "step": 2,
            "temperature": 55,
            "time": 1,
            "rate": 0,
            "vacuum": 0,
        }
    ]
}


#programs = {
#    "programs": [
#        {
#            "name": "Main",
#            "steps": [
#                {
#                    "step": 1,
#                    "temperature": 25,
#                    "time": 60,
#                    "rate": 0,
#                    "vacuum": True,
#                },
#                {
#                    "step": 2,
#                    "temperature": 55,
#                    "time": 60,
#                    "rate": 0,
#                    "vacuum": False,
#                },
#                {
#                    "step": 3,
#                    "temperature": 0,
#                    "time": 60,
#                    "rate": 0,
#                    "vacuum": False,
#                }
#            ]
#        }
#    ]
#}

programs = Programs()


def update_program(p):
    global programs
    print(type(p))
    print(type(programs))
    found = False
    i = 0
    for item in programs.programs:
        print(type(item))
        if item.name == p.name:
            programs.programs[i] = p
            found = True
            break
        i += 1
    if not found:
        programs.programs.append(p)
    s_str = json.dumps(programs.repr_json(), cls=ComplexEncoder)
    print(s_str)
    save_file("programs.json", s_str)


def load_programs():
    global programs
    programs = Programs()
    c = load_file("programs.json")
    j = json.loads(c)
    for item_p in j['programs']:
        program = Program()
        program.name = item_p['name']
        for item_s in item_p['steps']:
            step = Step(**item_s)
            program.steps.append(step)
        programs.programs.append(program)
    print(type(programs))
    print(json.dumps(programs.repr_json(), cls=ComplexEncoder))


def load_file(file):
    f = open(file, "r")
    contents = f.read()
    f.close()
    return contents


def save_file(file, value):
    f = open(file, "w")
    f.write(value)
    f.close()


def save():
    f = open("msg.json", "w")
    f.write(json.dumps(msg))
    f.close()


def load():
    global msg
    try:
        f = open("msg.json", "r")
        msg = json.loads(f.read())
        f.close()
    except FileNotFoundError:
        save()
    load_programs()


class Settings(object):
    def __init__(self):
        self._msg = 1

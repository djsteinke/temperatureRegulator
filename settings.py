import json

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


class Settings(object):
    def __init__(self):
        self._msg = 1

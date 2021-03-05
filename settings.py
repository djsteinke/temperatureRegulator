
msg = {
    "current": {
        "humidity": 20.0,
        "temperature": 75.0,
        "stepTemperature": 0.0,
        "step": 0,
        "stepTime": 0.0,
        "elapsedTime": 0.0,
        "heat": False,
        "vacuum": False
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


class Settings(object):
    def __init__(self):
        self._msg = 1

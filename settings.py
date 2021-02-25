
msg = {
    "current": {
        "humidity": 20,
        "temperature": 75.0,
        "stepTemperature": 0.0,
        "step": 0,
        "stepTime": 0.0,
        "elapsedTime": 0.0,
        "started": False
    },
    "program": [
        {
            "step": 1,
            "temperature": 35,
            "time": 1,
            "rate": 0
        },
        {
            "step": 3,
            "temperature": 0,
            "time": 1,
            "rate": 0
        },
        {
            "step": 2,
            "temperature": 55,
            "time": 1,
            "rate": 0
        }
    ]
}


class Settings(object):
    def __init__(self):
        self._msg = 1

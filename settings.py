
msg = {
    "current": {
        "temperature": 75,
        "step": 0,
        "stepTime": 0.0,
        "elapsedTime": 0.0
    },
    "program": [
        {
            "step": 1,
            "temperature": 150,
            "time": 1,
            "rate": 0
        },
        {
            "step": 3,
            "temperature": 160,
            "time": 1,
            "rate": 0
        },
        {
            "step": 2,
            "temperature": 160,
            "time": 1,
            "rate": 0
        }
    ]
}


class Settings(object):
    def __init__(self):
        self._msg = 1

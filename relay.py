import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Relay(object):
    def __init__(self, pin):
        self._on = False
        self._pin = pin
        GPIO.setup(self._pin, GPIO.OUT)
        GPIO.output(self._pin, GPIO.LOW)

    def on(self):
        # TODO turn on
        self._on = True
        GPIO.output(self._pin, GPIO.HIGH)

    def off(self):
        # TODO turn off
        self._on = False
        GPIO.output(self._pin, GPIO.LOW)

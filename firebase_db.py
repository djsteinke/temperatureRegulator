import firebase_admin
from firebase_admin import db
import time

databaseURL = "https://rn5notifications-default-rtdb.firebaseio.com/"
appKey = "tempReg"

cred_obj = firebase_admin.credentials.Certificate("/home/pi/firebaseKey.json")
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': databaseURL
})

ref = db.reference(appKey)
status = ref.child("status").get()
programs = ref.child("programs").get()


def save_status():
    ref.child("status").update(status)


def temperature(t=-100):
    if -100 < t != status['temperature']:
        status['temperature'] = t
    else:
        t = status['temperature']
    return t


def humidity(h=-1):
    if -1 < h != status['humidity']:
        status['humidity'] = h
    else:
        h = status['humidity']
    return h


def hold_temp():
    if "heat" in status:
        return status['heat']['tempSet']
    elif "program" in status:
        return status['program']['tempSet']
    else:
        return -1


def lamp_on(on=None):
    if on is not None and status["lampOn"] != on:
        status["lampOn"] = on
    else:
        on = status["lampOn"]
    return on


def pump_on(on=None):
    if on is not None and status["pumpOn"] != on:
        status["pumpOn"] = on
    else:
        on = status["pumpOn"]
    return on


def get_programs():
    return ref.get("programs")


def program(name=None, step=-1, steps=None):
    if name is not None:
        status['program'] = {}
        status['program']['name'] = name
        status['program']['step'] = step
        step_count = 0
        details = {}
        for key, value in steps:
            step_count += 1
            if int(key) == step:
                details = value
        status['program']['stepCnt'] = step_count
        status['program']['tempSet'] = details['tempSet']
        status['program']['pumpOn'] = details['pumpOn']
        status['program']['startTime'] = int(time.time())
        status['program']['endTime'] = int(time.time()) + details['runTime']
    else:
        del status['program']


def program_step(step, details):
    status['program']['step'] = step
    status['program']['tempSet'] = details['tempSet']
    status['program']['pumpOn'] = details['pumpOn']
    status['program']['startTime'] = int(time.time())
    status['program']['endTime'] = int(time.time()) + details['runTime']


def heat(run_time=-1, hold_t=-1):
    if run_time > 0:
        status['heat'] = {}
        status['heat']['startTime'] = int(time.time())
        status['heat']['endTime'] = int(time.time()) + run_time
        status['heat']['tempSet'] = hold_t
        status['heat']['timeSet'] = run_time
    else:
        ref.child('status').child('heat').update({})


def vacuum(run_time=-1):
    if run_time > 0:
        status['vacuum'] = {}
        status['vacuum']['startTime'] = int(time.time())
        status['vacuum']['endTime'] = int(time.time()) + run_time
        status['vacuum']['timeSet'] = run_time
    else:
        del status['vacuum']


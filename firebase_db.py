import firebase_admin
from firebase_admin import db
import time

databaseURL = "https://rn5notifications-default-rtdb.firebaseio.com/"
appKey = "tempReg"

cred_obj = firebase_admin.credentials.Certificate("/home/pi/firebaseKey.json")
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': databaseURL
})

ref = db.reference(appKey + "/status")
status = ref.get()


def temperature(t=-100):
    if -100 < t != status['temperature']:
        status['temperature'] = t
        ref.set(status)
    else:
        t = status['temperature']
    return t


def humidity(h=-1):
    if -1 < h != status['humidity']:
        status['humidity'] = h
        ref.set(status)
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
    if on is not None and status.child("lampOn").get() != on:
        status.child("lampOn").set(on)
    else:
        on = status.child("lampOn").get()
    return on


def pump_on(on=None):
    if on is not None and status.child("pumpOn").get() != on:
        status.child("pumpOn").set(on)
    else:
        on = status.child("pumpOn").get()
    return on


def get_programs():
    return ref.get("programs")


def heat(run_time=-1, hold_t=-1):
    h = status.child("heat")
    if run_time > 0:
        h.child("startTime").set(int(time.time()))
        h.child("endTime").set(int(time.time()) + run_time)
        h.child("tempSet").set(hold_t)
        h.child("timeSet").set(run_time)
    else:
        h.set({})


def vacuum(run_time=-1):
    v = status.child("vacuum")
    if run_time > 0:
        v.child("startTime").set(time.time())
        v.child("endTime").set(int(time.time()) + run_time)
        v.child("time").set(run_time)
    else:
        v.set({})



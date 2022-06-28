import firebase_admin
from firebase_admin import db
from os import getcwd

databaseURL = "https://rn5notifications-default-rtdb.firebaseio.com/"
appKey = "tempReg"

cred_obj = firebase_admin.credentials.Certificate("/home/pi/firebaseKey.json")
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': databaseURL
})

ref = db.reference("/" + appKey)


def lamp_on(on):
    ref.get("status")
    ref.child("lampOn").set(on)


def pump_on(on):
    ref.get("status")
    ref.child("pumpOn").set(on)


def get_programs():
    return ref.get("programs")


def heat(status):
    ref.get("status/heat")
    if status.heat_running:
        ref.child("startTime").set()
        ref.child("endTime").set()
        ref.child("tempSet").set(status.hold_temperature)
        ref.child("timeSet").set(status.step_time)
    else:
        ref.set({})


def vacuum(status):
    ref.get("status/vacuum")
    if status.vacuum_running:
        ref.child("startTime").set()
        ref.child("endTime").set()
        ref.child("time").set(status.vacuum_time_remaining)
    else:
        ref.set({})



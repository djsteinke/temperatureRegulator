import firebase_admin
from firebase_admin import db
from os import getcwd

databaseURL = "https://rn5notifications-default-rtdb.firebaseio.com/"
appKey = "tempReg"

cred_obj = firebase_admin.credentials.Certificate(getcwd() + "\\firebaseKey.json")
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL': databaseURL
	})

ref = db.reference("/" + appKey)


class FirebaseDb(object):
	def __init__(self):
		self._programs = ref.get("programs")
		self._history = None

	@property
	def programs(self):
		self._programs = ref.get("programs")
		print(self._programs)
		return self._programs

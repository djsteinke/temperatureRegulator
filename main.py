import logging
import socket

from flask import Flask, request, send_from_directory

from ComplexEncoder import ComplexEncoder
from static import get_logging_level
from hotbox import Hotbox
import json
import os
import subprocess
import firebase_db

app = Flask(__name__)

# create logger with 'spam_application'
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('log.log')
fh.setLevel(get_logging_level())
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

hotbox = Hotbox()


@app.route('/get/<option>')
def get(option):
    if option == "status":
        ret = get_response("status")
        s_str = json.dumps(hotbox.status.repr_json(), cls=ComplexEncoder)
        s_j = json.loads(s_str)
        ret['status'] = s_j
        return ret, 200


@app.route('/pi/<action>')
def pi_action(action):
    ret = get_response("pi")
    if action == "r" or action == "h":
        ret['value'] = action
        cmd = f"sudo shutdown -{action} now"
        subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    else:
        ret['code'] = 400
        ret['value'] = action
        ret['error'] = "Invalid action."
    return ret, 200


@app.route('/upload', methods=['POST'])
def upload():
    x = request.json
    logger.debug('/upload\n' + json.dumps(x))
    ret = get_response('upload')
    if 'programs' in x:
        hotbox.settings.process_programs_json(x)
        ret['value'] = 'Programs loaded.'
    else:
        hotbox.settings.update_program(x)
        ret['value'] = f'Program {x["name"]} loaded.'
    return ret, 200


@app.route('/run')
def run():
    tp = request.args.get('type', default='', type=str)
    temp = request.args.get('temp', default=0.0, type=float)
    time = request.args.get('time', default=0, type=int)
    program = request.args.get('program', default='', type=str)
    ret = get_response("run")
    ret['value'] = tp
    if tp == "program":
        if not hotbox.status.program_running:
            r = hotbox.start_program(program)
            ret['code'] = r[0]
            if r[0] != 200:
                ret['error'] = r[1]
            else:
                ret['value'] = r[1]
        else:
            ret['code'] = 301
            ret['error'] = "Program already running."
    elif tp == "heat" and temp > 0 and time > 0:
        if not hotbox.status.heat_running:
            hotbox.start_heat(temp, time * 60)
        else:
            ret['code'] = 301
            ret['error'] = "Heat already running."
    elif tp == "vacuum" and time > 0:
        if not hotbox.status.vacuum_running:
            hotbox.start_vacuum(time * 60)
        else:
            ret['code'] = 301
            ret['error'] = "Vacuum already running."
    return ret, 200


@app.route('/cancel')
def cancel():
    tp = request.args.get('type', default='', type=str)
    ret = get_response("cancel")
    ret['value'] = tp
    if tp == "program":
        hotbox.end_program()
    elif tp == "heat":
        hotbox.stop_heat()
    elif tp == "vacuum":
        hotbox.stop_vacuum()
    return ret, 200


def get_response(response_type):
    return {"code": 200,
            "type": response_type,
            "value": None,
            "error": None,
            "message": None,
            "status": {}}


def get_c_from_f(f):
    c = f-32
    c = c/1.8
    return c


def get_f_from_c(c):
    return c*1.8 + 32


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    host_name = socket.gethostbyname(socket.gethostname())
    logger.info("machine host_name[" + host_name + "]")
    print(host_name + "[" + host_name[0: 3] + "]")
    if host_name[0: 3] == "192" or host_name[0: 3] == "127":
        host_name = "192.168.0.151"
    else:
        host_name = "localhost"
    logger.info("app host_name[" + host_name + "]")
    hotbox.settings.load()
    hotbox.start()
    db = firebase_db.FirebaseDb()
    firebase_db.heat(True)
    app.run(host=host_name, port=1983)

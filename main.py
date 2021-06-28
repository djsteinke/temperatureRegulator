import logging
import socket

from flask import Flask, request, send_from_directory

from ComplexEncoder import ComplexEncoder
from static import get_logging_level
from settings import msg, load, update_program
from define.program import Program
from hot_box import HotBox
import json
import os

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

hot_box = HotBox()


@app.route('/programs/add/<val>')
def programs(val):
    update_program(json.loads(val))


@app.route('/get/<option>')
def get(option):
    if option == "status":
        ret = get_response("status")
        s_str = json.dumps(hot_box.status.repr_json(), cls=ComplexEncoder)
        print(s_str)
        s_j = json.loads(s_str)
        ret['status'] = s_j
        return ret, 200


@app.route('/pi/<action>')
def pi_action(action):
    cmd = "sudo shutdown -"
    ret = get_response("pi")
    if action == "r" or action == "h":
        ret['value'] = action
        os.system(f"{cmd} {action}")
    else:
        ret['code'] = 400
        ret['value'] = action
        ret['error'] = "Invalid action."
    return ret, 200


@app.route('/upload', methods=['POST'])
def upload():
    x = request.json
    p = Program(**x)
    update_program(p)
    ret = get_response('upload')
    ret['value'] = f'Program "{p.name}" updated.'
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
        if not hot_box.status.prog_running:
            hot_box.program(msg['program'])
            hot_box.start_program(program)
        else:
            ret['code'] = 301
            ret['error'] = "Program already running."
    elif tp == "heat" and temp > 0 and time > 0:
        if not hot_box.status.heat_running:
            hot_box.heat_on(temp, time*60)
        else:
            ret['code'] = 301
            ret['error'] = "Heat already running."
    elif tp == "vacuum" and time > 0:
        if not hot_box.status.vacuum_running:
            hot_box.vacuum_on(time*60)
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
        hot_box.program(msg['program'])
        hot_box.end_program()
    elif tp == "heat":
        hot_box.heat_cancel()
    elif tp == "vacuum":
        hot_box.vacuum_cancel()
    return ret, 200


def get_response(response_type):
    return {"code": 200,
            "type": response_type,
            "value": None,
            "error": None,
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
    load()
    app.run(host=host_name, port=1983)

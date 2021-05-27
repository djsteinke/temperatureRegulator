import logging
import socket
import re

from flask import Flask, request, send_from_directory

from static import get_logging_level
from settings import msg, save, load
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


@app.route('/get/<option>')
def get(option):
    if option == "status":
        ret = get_response("status")
        s_str = json.dumps(hot_box.status.__dict__)
        s_str = re.sub("\"_", "\"", s_str)
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
    y = json.dumps(x)
    print(y)
    logger.debug("upload() program[" + y + "]")
    msg['program'] = x
    save()
    ret = get_response('upload')
    return ret, 200


@app.route('/run')
def run():
    tp = request.args.get('type', default='', type=str)
    temp = request.args.get('temp', default=0.0, type=float)
    time = request.args.get('time', default=0, type=int)
    prog = request.args.get('filter', default='', type=str)
    ret = get_response("run")
    ret['value'] = tp
    if tp == "program":
        hot_box.program(msg['program'])
        hot_box.start_program(prog)
    elif tp == "heat":
        if hot_box.status.heat:
            hot_box.heat_off()
        else:
            hot_box.heat_on(temp, time*60)
    elif tp == "vacuum":
        if hot_box.status.vacuum:
            hot_box.vacuum_off()
        else:
            hot_box.vacuum_on(time*60)
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

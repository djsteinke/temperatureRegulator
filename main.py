import logging
import socket

import RPi.GPIO as GPIO

from flask import Flask, request, jsonify, send_from_directory, render_template

from static import get_logging_level, get_temperature
from timer import Timer
from program import Program, heat
from settings import msg, save, load
from vacuum import Vacuum
from relay import Relay
import json
import os

app = Flask(__name__)
currentTemp = 0
current_set_temp = 0

p = Program()
t = Timer()

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

v = Vacuum()


def run_program(action):
    global p
    logger.debug("run_program(" + action + ")")
    if action == "start":
        if not p.is_running():
            print("Program started")
            logger.debug("run_program() Program Started")
            p.run()
    elif action == "stop":
        if p.is_running():
            print("Program stopped")
            logger.debug("run_program() Program Stopped")
            p.stop()


@app.route('/')
def current_settings():
    logger.debug("current_settings() msg[" + json.dumps(msg, indent=2) + "]")
    get_temperature()
    return json.dumps(msg), 200


@app.route('/pi/<action>')
def pi_action(action):
    cmd = "sudo shutdown -"
    if action == "r" or action == "h":
        os.system(f"sudo shutdown -{action}")
    else:
        return jsonify(message="Error",
                       statusCode=400,
                       data="Invalid action."), 400
    return jsonify(message="Success",
                   statusCode=200,
                   data=action), 200


@app.route('/getTemp')
def get_temp():
    logger.debug("get_temp() temperature[" + str(msg['current']['temperature']) + "]")
    get_temperature()
    return json.dumps(msg), 200


@app.route('/setTemp/<t>')
def set_temp(temp):
    msg["current"]["stepTemperature"] = int(temp)
    logger.debug("set_temp() temperature[" + temp + "]")
    return jsonify(message="Success",
                   statusCode=200,
                   data=int(temp)), 200


@app.route('/upload', methods=['POST'])
def upload():
    x = request.json
    y = json.dumps(x)
    print(y)
    logger.debug("upload() program[" + y + "]")
    msg['program'] = x
    save()
    return jsonify(message="Success",
                   statusCode=200,
                   data=y), 200


@app.route('/timer/<action>')
def timer(action):
    logger.debug("timer(" + action + ")")
    if action == "start":
        t.start()
    elif action == "stop":
        t.stop()
    return jsonify(message="Success",
                   statusCode=200,
                   data=action), 200


@app.route('/vacuum/<action>')
def vacuum(action):
    logger.debug("vacuum(" + action + ")")
    if action == "start" and not v.is_started():
        v.start()
        logger.debug("vacuum.start()")
    elif action == "stop" and v.is_started():
        v.stop()
        logger.debug("vacuum.stop()")
    return jsonify(message="Success",
                   statusCode=200,
                   data=action), 200


@app.route('/program/<action>')
def program(action):
    logger.debug("program(" + action + ")")
    run_program(action)
    return jsonify(message="Success",
                   statusCode=200,
                   data=action), 200


@app.route('/name/<name>')
def fun(name):
    logger.debug("fun(" + name + ")")
    return '''

<html>    
    <head>
    <style>
    body{
        font-family:"Roboto";
        text-align:center;
    }
    </style>
        <title>''' + name + '''</title>
    </head>
    <body>
        <h1>Hello, ''' + name + '''!</h1>
    </body>
</html>'''


def get_c_from_f(f):
    c = f-32
    c = c/1.8
    return c


def get_f_from_c(c):
    return c*1.8 + 32


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


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
    # app.run(ssl_context='adhoc', host=host_name, port=1983)
    app.run(host=host_name, port=1983)

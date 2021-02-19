import logging
import socket

from flask import Flask, request, jsonify, send_from_directory, render_template
from timer import Timer
from program import Program
from settings import msg
import json
import os

app = Flask(__name__)
currentTemp = 0
current_set_temp = 0

p = Program()
t = Timer()

# create logger with 'spam_application'
logger = logging.getLogger('temperatureRegulator')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
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
    logger.debug("current_settings() msg[" + msg + "]")
    return msg


@app.route('/getTemp')
def get_temp():
    logger.debug("get_temp() temperature[" + str(msg['current']['temperature']) + "]")
    return str(msg['current']['temperature'])


@app.route('/setTemp/<t>')
def set_temp(temp):
    msg["setTemp"] = int(temp)
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
    app.run(host=host_name, port=1983)

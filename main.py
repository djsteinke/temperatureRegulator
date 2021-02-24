import logging
import socket
import time

import RPi.GPIO as GPIO
import smbus

from flask import Flask, request, jsonify, send_from_directory, render_template

from static import get_logging_level
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

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pin = 23
pin_state = 0
GPIO.setup(pin, GPIO.OUT)
GPIO.output(pin, GPIO.LOW)

bus = smbus.SMBus(1)
config = [0x08, 0x00]


def run_program(acton):
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
    return msg


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
    global data
    logger.debug("get_temp() temperature[" + str(msg['current']['temperature']) + "]")
    bus.write_i2c_block_data(0x38, 0xE1, config)
    byt = bus.read_byte(0x38)
    print(byt & 0x68)
    MeasureCmd = [0x33, 0x00]
    bus.write_i2c_block_data(0x38, 0xAC, MeasureCmd)
    time.sleep(0.5)
    data = bus.read_i2c_block_data(0x38, 0x00)
    temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
    ctemp = ((temp*200)/1048576) - 50
    tmp = ((data[1] << 16) | (data[2] << 8) | data[3] >> 4)
    ctmp = int(tmp * 100 / 1048576)
    return jsonify(message="Success",
                   statusCode=200,
                   temp=ctemp,
                   humidity=ctmp), 200


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


@app.route('/led/<pin_in>/<action>')
def led(pin_in, action):
    global pin_state
    GPIO.setup(int(pin_in), GPIO.OUT)
    if action == "on":
        GPIO.output(int(pin_in), GPIO.HIGH)
    else:
        GPIO.output(int(pin_in), GPIO.LOW)
    # pin_state = GPIO.input(pin)
    logger.debug(f"led({action}) state({pin_state})")
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

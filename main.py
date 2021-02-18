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


def run_program(action):
    global p
    if action == "start":
        if not p.is_running():
            print("Program started")
            p.run()
    elif action == "stop":
        if p.is_running():
            print("Program stopped")
            p.stop()


@app.route('/')
def current_settings():
    return msg


@app.route('/getTemp')
def get_temp():
    return str(msg['current']['temperature'])


@app.route('/setTemp/<t>')
def set_temp(temp):
    msg["setTemp"] = int(temp)
    return jsonify(message="Success",
                   statusCode=200,
                   data=int(temp)), 200


@app.route('/upload', methods=['POST'])
def upload():
    x = request.json
    y = json.dumps(x)
    print(y)
    msg['program'] = x
    return jsonify(message="Success",
                   statusCode=200,
                   data=y), 200


@app.route('/timer/<action>')
def timer(action):
    if action == "start":
        t.start()
    elif action == "stop":
        t.stop()
    return jsonify(message="Success",
                   statusCode=200,
                   data=action), 200


@app.route('/program/<action>')
def program(action):
    run_program(action)
    return jsonify(message="Success",
                   statusCode=200,
                   data=action), 200


@app.route('/name/<name>')
def fun(name):
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
    print(host_name + "[" + host_name[0: 3] + "]")
    if host_name[0: 3] != "192":
        host_name = "localhost"
    app.run(host=host_name, port=1983)

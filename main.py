from flask import Flask, request, jsonify
import json

app = Flask(__name__)

currentTemp = 0
current_set_temp = 0
msg = json.loads('{"temp":95,"setTemp":120}')


@app.route('/')
def current_settings():
    global msg
    return msg


@app.route('/getTemp')
def get_temp():
    global msg
    return str(msg["setTemp"])


@app.route('/setTemp/<t>')
def set_temp(t):
    global msg
    msg["setTemp"] = int(t)
    return jsonify(isError=False,
                   message="Success",
                   statusCode=200,
                   data=int(t)), 200


@app.route('/upload', methods=['POST'])
def upload():
    try:
        x = request.json
        y = json.dumps(x)
        print(y)
        return jsonify(isError=False,
                       message="Success",
                       statusCode=200,
                       data=y), 200
    except ValueError:
        print("JSON validation error")
        return jsonify(isError=True,
                       message="Error",
                       statusCode=400,
                       data='Malformed JSON'), 400


def get_c_from_f(f):
    c = f-32
    c = c/1.8
    return c


if __name__ == '__main__':
    app.run()

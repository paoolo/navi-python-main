import os
import time

from flask import Flask, render_template

from flask.ext.socketio import SocketIO, emit


pwd = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=pwd)
socket_io = SocketIO(app)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    socket_io.run(app)
    while True:
        emit('log_response', {'data': 'Connected'}, broadcast=True)
        time.sleep(10)
import os
import logging
import threading

from flask import Flask, render_template

from flask.ext.socketio import SocketIO


logging.basicConfig()

_pwd = os.path.abspath(__file__)

for i in range(4):
    _pwd = os.path.dirname(_pwd)

_pwd += '/web'
_app = Flask(__name__, template_folder=_pwd)
_socket_io = SocketIO(_app)


@_app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@_app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@_app.route('/')
def index():
    return render_template('index.html')


def _run():
    _socket_io.run(_app)


def start():
    _thread = threading.Thread(target=_run)
    _thread.start()


def emit(*args, **kwargs):
    _socket_io.emit(*args, **kwargs)


def send(*args, **kwargs):
    _socket_io.send(*args, **kwargs)
import multiprocessing
import os
import logging
import threading

from amber.common import runtime

from flask import Flask, render_template
from tornado import websocket, ioloop, web


logging.basicConfig()

_pwd = os.path.abspath(__file__)

for i in range(4):
    _pwd = os.path.dirname(_pwd)

_pwd += '/web'

_app_flask = Flask(__name__, template_folder=_pwd)


@_app_flask.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@_app_flask.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@_app_flask.route('/')
def index():
    return render_template('index.html')


def _run_flask():
    _app_flask.run(host='0.0.0.0')


flask_thread = None


def _stop_flask():
    if flask_thread is not None:
        flask_thread.terminate()
        flask_thread.join()


_sockets = []


class WebSocket(websocket.WebSocketHandler):
    def open(self):
        _sockets.append(self)

    def on_close(self):
        _sockets.remove(self)


def _run_tornado():
    application = web.Application([
        (r"/", WebSocket),
    ])
    application.listen(8888)
    ioloop.IOLoop.instance().start()


def _stop_tornado():
    ioloop.IOLoop.instance().stop()


def emit(data):
    for socket in _sockets:
        socket.write_message(data)


def send(data):
    for socket in _sockets:
        socket.write_message(data)


def start():
    _tornado_thread = threading.Thread(target=_run_tornado)
    _tornado_thread.start()
    runtime.add_shutdown_hook(_stop_tornado)

    web.flask_thread = multiprocessing.Process(target=_run_flask)
    flask_thread.start()
    runtime.add_shutdown_hook(_stop_flask)

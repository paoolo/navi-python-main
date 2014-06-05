import os
import logging
import threading
import urllib2
import time

from amber.common import runtime
from flask import Flask, render_template, request
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


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@_app_flask.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


def _run_flask():
    _app_flask.run(host='0.0.0.0')


def _stop_flask():
    req = urllib2.Request('http://localhost:5000/shutdown', '')
    response = urllib2.urlopen(req)
    result = response.read()
    print result


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

    _flask_thread = threading.Thread(target=_run_flask)
    _flask_thread.start()
    runtime.add_shutdown_hook(_stop_flask)


if __name__ == '__main__':
    start()
    import random

    while True:
        emit({'data': 'test', 'target': 'driver', 'x': int(random.random() * 100), 'y': int(random.random() * 100)})
        time.sleep(1)
import os
import logging
import threading
import urllib2
import time

from amber.common import runtime
from navi.tools import config
from flask import Flask, render_template, request
from tornado import websocket, ioloop, web

from flask import request


logging.basicConfig()

_config = {}

_pwd = os.path.abspath(__file__)

for i in range(4):
    _pwd = os.path.dirname(_pwd)

_pwd += '/web'

_app_flask = Flask(__name__, template_folder=_pwd, static_folder=os.path.join(_pwd, 'static'), static_url_path='')


@_app_flask.errorhandler(404)
def not_found_error(_):
    return render_template('404.html'), 404


@_app_flask.errorhandler(500)
def internal_error(_):
    return render_template('500.html'), 500


@_app_flask.route('/')
def index():
    return render_template('index.html')


@_app_flask.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'save_button' in request.form:
        values = dict(request.form.items())
        del values['save_button']
        for key, value in values.items():
            config.set(key, value)

    elif 'cancel_button' in request.form:
        # nothing to do here
        pass

    elif 'reload_button' in request.form:
        if 'app' in _config:
            _config['app'].reload()

    kwargs = config.get_all()
    return render_template('settings.html', **kwargs)


@_app_flask.route('/static/<path:path>')
def static_proxy(path):
    return _app_flask.send_static_file(path)


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


def start(_app=None):
    if _app is not None:
        _config['app'] = _app

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
        time.sleep(0.07)
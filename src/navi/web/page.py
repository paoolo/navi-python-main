import logging
import urllib2

import os
from flask import Flask, render_template
from flask import request


logging.basicConfig()

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


_global = {}


@_app_flask.route('/')
def index():
    kwargs = {'chain': _global['chain']} if 'chain' in _global else {}
    return render_template('index.html', **kwargs)


@_app_flask.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'save_button' in request.form:
        chain = _global['chain'].to_dict()
        values = dict(request.form.items())
        del values['save_button']
        print values
        for key, value in values.items():
            component_name, parameter = str(key).split('_', 1)
            component = chain[component_name]
            setattr(component, parameter, value)

    kwargs = {'chain': _global['chain']} if 'chain' in _global else {}
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


def run_flask(chain):
    _global['chain'] = chain
    _app_flask.run(host='0.0.0.0')


def stop_flask():
    req = urllib2.Request('http://localhost:5000/shutdown', '')
    response = urllib2.urlopen(req)
    response.read()
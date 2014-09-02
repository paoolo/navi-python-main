import logging
import urllib2

from navi.app import main
import os
from flask import Flask, render_template
from flask import request


_STOP = '/stop'

logging.basicConfig()

_pwd = os.path.abspath(__file__)

for i in range(4):
    _pwd = os.path.dirname(_pwd)

_pwd += '/web'

_app_flask = Flask(__name__, template_folder=_pwd, static_folder=os.path.join(_pwd, 'static'), static_url_path='')

_global = {}


@_app_flask.errorhandler(404)
def not_found_error(_):
    return render_template('404.html'), 404


@_app_flask.errorhandler(500)
def internal_error(_):
    return render_template('500.html'), 500


@_app_flask.route('/')
def index():
    return render_template('index.html')


@_app_flask.route('/dashboard')
def dashboard():
    chain = _global['registry']['chain'] if 'registry' in _global and 'chain' in _global['registry'] else []
    kwargs = {'chain': chain}
    return render_template('dashboard.html', **kwargs)


def save_settings(chain, values):
    chain = dict(zip(map(lambda e: e.key, chain), chain))
    for key, parameter_value in values.items():
        component_key, parameter_name = str(key).split('_', 1)
        if component_key in chain:
            component = chain[component_key]
            setattr(component, parameter_name, parameter_value)


@_app_flask.route('/settings', methods=['GET', 'POST'])
def settings():
    chain = _global['registry']['chain'] if 'registry' in _global and 'chain' in _global['registry'] else []

    if 'save_button' in request.form:
        values = dict(request.form.items())
        del values['save_button']
        save_settings(chain, values)

    kwargs = {'chain': chain}
    return render_template('settings.html', **kwargs)


@_app_flask.route('/static/<path:path>')
def static_proxy(path):
    return _app_flask.send_static_file(path)


@_app_flask.route(_STOP, methods=['POST'])
def stop():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'


@_app_flask.route('/amber_connect', methods=['GET', 'POST'])
def amber_connect():
    if request.method == 'POST':
        values = dict(request.form.items())
        if 'address' in values:
            main.connect_amber(values['address'])
    return index()


@_app_flask.route('/amber_disconnect', methods=['GET', 'POST'])
def restart_app():
    if request.method == 'POST':
        main.disconnect_amber()
    return index()


def run_flask(registry):
    _global['registry'] = registry
    _app_flask.run(host='0.0.0.0')


def stop_flask():
    print 'try to stop flask...'
    req = urllib2.Request('http://localhost:5000%s' % _STOP, '')
    response = urllib2.urlopen(req)
    response.read()
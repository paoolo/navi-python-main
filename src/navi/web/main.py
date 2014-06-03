import os

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


@app.route('/bla')
def bla():
    return 'Test'


@socket_io.on('my event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']})


@socket_io.on('my broadcast event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)


@socket_io.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected'})


@socket_io.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socket_io.run(app)
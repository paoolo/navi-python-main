__author__ = 'paoolo'

from flask import Flask, render_template

from flask.ext.socketio import SocketIO, emit


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket_io = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socket_io.on('my event')
def test_message(message):
    emit('my response', {'data': 'got it!'})


if __name__ == '__main__':
    socket_io.perform(app)
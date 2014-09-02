import logging

from tornado import websocket, ioloop, web

logging.basicConfig()

_sockets = []


class WebSocket(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        _sockets.append(self)

    def on_close(self):
        _sockets.remove(self)


def run_tornado(_):
    application = web.Application([
        (r"/", WebSocket),
    ])
    application.listen(8888)
    ioloop.IOLoop.instance().start()


def stop_tornado():
    print 'try to stop tornado...'
    ioloop.IOLoop.instance().stop()


def emit(data):
    for socket in _sockets:
        socket.write_message(data)


def send(data):
    for socket in _sockets:
        socket.write_message(data)
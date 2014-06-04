from tornado import web, ioloop, websocket

GLOBALS = {
    'sockets': []
}


class MainHandler(web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class ClientSocket(websocket.WebSocketHandler):
    def open(self):
        GLOBALS['sockets'].append(self)
        print "WebSocket opened"

    def on_close(self):
        print "WebSocket closed"
        GLOBALS['sockets'].remove(self)


class Announcer(web.RequestHandler):
    def get(self, *args, **kwargs):
        data = self.get_argument('data')
        for socket in GLOBALS['sockets']:
            socket.write_message(data)
        self.write('Posted')


application = web.Application([
    (r"/", MainHandler),
    (r"/socket", ClientSocket),
    (r"/push", Announcer),
])

if __name__ == "__main__":
    application.listen(8888)
    ioloop.IOLoop.instance().start()


"""
$(document).ready(function () {
    var ws = new WebSocket("ws://localhost:8888/socket");
    ws.onmessage = function(event) {
        alert(event);
        alert(event.data);
    }
});
"""
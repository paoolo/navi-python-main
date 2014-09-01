import socket
import struct
import threading
import traceback

from amber.common import runtime
from navi.proto import controlmsg_pb2
from navi.components.component import Component


__author__ = 'paoolo'


class Manual(Component):
    """
    Used to manual.
    """

    def __init__(self):
        super(Manual, self).__init__()

        self._alive = True
        self._left = 0
        self._right = 0

        self._address = '0.0.0.0'
        self._port = 1234

        self._receiver_thread = threading.Thread(target=self._receiver_loop)
        runtime.add_shutdown_hook(self._terminate)
        self._receiver_thread.start()

    def _receiver_loop(self):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((self._address, self._port))
        self.__server_socket.listen(5)

        try:
            while self._alive:
                print 'receiver loop: wait for client'
                (client_socket, address) = self.__server_socket.accept()

                print 'receiver loop: client connected'
                try:
                    while self._alive:
                        data_to_read = client_socket.recv(2)
                        if len(data_to_read) <= 0:
                            break

                        data_to_read = struct.unpack('H', data_to_read)[0]
                        if data_to_read > 0:
                            data = client_socket.recv(data_to_read)
                            msg = controlmsg_pb2.ControlMessage()
                            msg.ParseFromString(data)

                            if msg.type == controlmsg_pb2.SET:
                                self._set(msg.left, msg.right)

                            elif msg.type == controlmsg_pb2.CHANGE:
                                self._change(msg.left, msg.right)

                    print 'receiver loop: client disconnected'
                    self._set(0, 0)

                except BaseException as e:
                    traceback.print_exc()
                    print 'receiver loop: client error: %s' % str(e)

        except BaseException as e:
            traceback.print_exc()
            print 'receiver loop: server down: %s' % str(e)

        print 'receiver loop: stop'

    def _set(self, left, right):
        self._left, self._right = left, right

    def _change(self, left, right):
        self._left += left
        self._right += right

    def _terminate(self):
        print 'terminate manual'

        self._alive = False
        # noinspection PyBroadException
        try:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('127.0.0.1', self._port))
            self.__server_socket.close()
        except BaseException:
            pass

    def modify(self, left, right):
        return self._left, self._right

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, val):
        self._address = str(val)

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, val):
        self._port = int(val)
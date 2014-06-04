import socket
import threading
import time
import struct
import traceback

from amber.common import amber_client, runtime
from amber.hokuyo import hokuyo
from amber.roboclaw import roboclaw

from navi.proto import controlmsg_pb2
from navi.tools import component, config


__author__ = 'paoolo'

ADDRESS = str(config.ADDRESS)
PORT = int(config.PORT)


class App(object):
    def __init__(self, amber_ip):
        self.__cond = threading.Condition()
        self.__server_socket = None

        self.__amber_ip = amber_ip
        self.__amber_client = None

        self.__hokuyo, self.__roboclaw = None, None
        self.__alive = True

        self.__chain = None
        self.__manual, self.__receiver_thread = None, None

    def __receiver_loop(self):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((ADDRESS, PORT))
        self.__server_socket.listen(5)

        try:
            while self.__alive:
                (client_socket, address) = self.__server_socket.accept()
                print 'manual_thread: client connected'

                try:
                    while self.__alive:
                        data_to_read = client_socket.recv(2)
                        if len(data_to_read) <= 0:
                            break

                        data_to_read = struct.unpack('H', data_to_read)[0]
                        if data_to_read > 0:
                            data = client_socket.recv(data_to_read)
                            msg = controlmsg_pb2.ControlMessage()
                            msg.ParseFromString(data)

                            if msg.type == controlmsg_pb2.SET:
                                self.__manual.set(msg.left, msg.right)

                            elif msg.type == controlmsg_pb2.CHANGE:
                                self.__manual.change(msg.left, msg.right)

                    print 'manual_thread: client disconnected'
                    self.__manual.set(0, 0)

                except BaseException as e:
                    traceback.print_exc()
                    print 'manual_thread: client error: %s' % str(e)

        except BaseException as e:
            traceback.print_exc()
            print 'manual_thread: server down: %s' % str(e)

        print 'manual thread stop'

    def __main_loop(self):
        try:
            while self.__alive:
                self.__chain.perform()

                time.sleep(0.07)
        except BaseException as e:
            traceback.print_exc()
            print 'main_loop exception: %s' % str(e)

        print 'auto thread stop'

    def __configure_robo(self):
        self.__amber_client = amber_client.AmberClient(self.__amber_ip)

        self.__hokuyo = hokuyo.HokuyoProxy(self.__amber_client, 0)
        self.__roboclaw = roboclaw.RoboclawProxy(self.__amber_client, 0)

    def __configure_chain(self):
        rodeo_swap = component.RodeoSwap()
        self.__hokuyo.subscribe(rodeo_swap)
        self.__chain.append(rodeo_swap)

        self.__chain.append(component.Back())

        controller = component.Controller()
        self.__hokuyo.subscribe(controller)
        self.__chain.append(controller)

        self.__chain.append(component.Stop())
        # self.__chain.append(component.PID(self.__roboclaw))
        self.__chain.append(component.Driver(self.__roboclaw))

    def manual(self):
        self.__configure_robo()

        self.__chain = component.Chain()
        self.__manual = component.Manual()
        self.__chain.append(self.__manual)
        self.__configure_chain()

        self.__receiver_thread = threading.Thread(target=self.__receiver_loop)
        self.__receiver_thread.start()

        runtime.add_shutdown_hook(self.terminate)
        self.__main_loop()

    def auto(self):
        self.__configure_robo()

        self.__chain = component.Chain()
        self.__chain.append(component.Randomize())
        self.__configure_chain()

        self.__main_loop()

    def terminate(self):
        print 'terminate app'

        self.__alive = False
        # noinspection PyBroadException
        try:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('127.0.0.1', PORT))
            self.__server_socket.close()
        except BaseException:
            pass

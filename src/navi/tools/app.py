import socket
import threading
import time
import struct
import traceback

from amber.common import amber_client
from amber.hokuyo import hokuyo
from amber.roboclaw import roboclaw

from navi.proto import controlmsg_pb2
from navi.tools import agent


__author__ = 'paoolo'

ADDRESS = '0.0.0.0'
PORT = 1234


class App(object):
    def __init__(self, amber_ip):
        self.__amber_ip = amber_ip
        self.__cond = threading.Condition()

        self.__server_socket = None
        self.__client = None
        self.__laser, self.__robo = None, None
        self.__eye, self.__driver, self.__controller = None, None, None
        self.__alive = True
        self.__networking_thread, self.__scanning_thread = None, None

    def __networking_loop(self):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((ADDRESS, PORT))
        self.__server_socket.listen(5)

        try:
            while self.__alive:
                (client_socket, address) = self.__server_socket.accept()
                print 'networking_thread: client connected'

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
                                self.__controller.set(msg.left, msg.right)
                            elif msg.type == controlmsg_pb2.CHANGE:
                                self.__controller.change(msg.left, msg.right)

                    print 'networking_thread: client disconnected'
                    self.__controller.set(0, 0)

                except BaseException as e:
                    traceback.print_exc()
                    print 'networking_thread: client error: %s' % str(e)

        except BaseException as e:
            traceback.print_exc()
            print 'networking_thread: server down: %s' % str(e)

        print 'networking thread stop'

    def __scanning_loop(self):
        try:
            while self.__alive:
                self.__eye.run()

                time.sleep(0.9)
        except BaseException as e:
            traceback.print_exc()
            print 'scanning_thread: laser down: %s' % str(e)

        print 'scanning thread stop'

    def __controller_driver_thread(self):
        try:
            while self.__alive:
                self.__controller.run()
                self.__driver.run()

                time.sleep(0.1)
        except BaseException as e:
            traceback.print_exc()
            print 'main_thread: main down: %s' % str(e)

        print 'controller driver thread stop'

    def __configure_robo(self):
        self.__client = amber_client.AmberClient(self.__amber_ip)

        # FIXME(paoolo); what is the device_id=0?
        self.__laser = hokuyo.HokuyoProxy(self.__client, 0)
        self.__robo = roboclaw.RoboclawProxy(self.__client, 0)

        self.__eye = agent.Eye(self.__laser)
        self.__driver = agent.Driver(self.__robo)
        self.__controller = agent.Controller(self.__eye, self.__driver)

    def main(self):
        self.__configure_robo()

        self.__networking_thread = threading.Thread(target=self.__networking_loop)
        self.__networking_thread.start()
        self.__scanning_thread = threading.Thread(target=self.__scanning_loop)
        self.__scanning_thread.start()

        self.__controller_driver_thread()

    def terminate(self):
        print 'terminate app'

        self.__alive = False
        # FIXME(paoolo); how ugly is this!
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('127.0.0.1', PORT))
        self.__server_socket.close()
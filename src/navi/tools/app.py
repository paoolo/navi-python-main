import socket
import time
import struct
import thread
import traceback

from amber.common import amber_client
from amber.hokuyo import hokuyo
from amber.roboclaw import roboclaw

from navi.proto import controlmsg_pb2
from navi.tools import agent


__author__ = 'paoolo'

ADDRESS = '0.0.0.0'
PORT = 1234


def networking_thread(controller):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ADDRESS, PORT))
    server_socket.listen(5)

    try:
        # FIXME(paoolo): replace True for sth other
        while True:
            (client_socket, address) = server_socket.accept()
            print 'networking_thread: client connected'

            try:
                # FIXME(paoolo): replace True for sth other
                while True:
                    data_to_read = client_socket.recv(2)
                    if len(data_to_read) <= 0:
                        break

                    data_to_read = struct.unpack('H', data_to_read)[0]
                    if data_to_read > 0:
                        data = client_socket.recv(data_to_read)
                        msg = controlmsg_pb2.ControlMessage()
                        msg.ParseFromString(data)

                        if msg.type == controlmsg_pb2.SET:
                            controller.set(msg.left, msg.right)
                        elif msg.type == controlmsg_pb2.CHANGE:
                            controller.change(msg.left, msg.right)

                print 'networking_thread: client disconnected'
                controller.set(0, 0)

            except BaseException as e:
                traceback.print_exc()
                print 'networking_thread: client error: %s' % str(e)

    except BaseException as e:
        traceback.print_exc()
        print 'networking_thread: server down: %s' % str(e)


def scanning_thread(eye):
    try:
        # FIXME(paoolo): replace True for sth other
        while True:
            eye.run()
    except BaseException as e:
        traceback.print_exc()
        print 'scanning_thread: laser down: %s' % str(e)


def main_thread(controller, driver):
    try:
        # FIXME(paoolo): replace True for sth other
        while True:
            controller.run()
            driver.run()
            time.sleep(0.1)
    except BaseException as e:
        traceback.print_exc()
        print 'main_thread: main down: %s' % str(e)


def configure_robo(amber_ip):
    client = amber_client.AmberClient(amber_ip)

    # FIXME(paoolo); what is the device_id=0?
    laser = hokuyo.HokuyoProxy(client, 0)
    robo = roboclaw.RoboclawProxy(client, 0)

    eye = agent.Eye(laser)
    driver = agent.Driver(robo)
    controller = agent.Controller(eye, driver)

    return eye, driver, controller


def main(amber_ip):
    eye, driver, controller = configure_robo(amber_ip)

    thread.start_new_thread(networking_thread, (controller, ))
    thread.start_new_thread(scanning_thread, (eye, ))

    main_thread(controller, driver)
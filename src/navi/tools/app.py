import socket
import time
import struct
import thread
import traceback

from driver import hokuyo
from driver import roboclaw
from proto import controlmsg_pb2
from tools import agent


__author__ = 'paoolo'

REAR_RC_ADDRESS = 128
FRONT_RC_ADDRESS = 129

MOTORS_MAX_QPPS = 13800
MOTORS_P_CONST = 65536
MOTORS_I_CONST = 32768
MOTORS_D_CONST = 16384

ADDRESS = '0.0.0.0'
PORT = 1234


def networking_thread(controller):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ADDRESS, PORT))
    server_socket.listen(5)

    try:
        while True:
            (client_socket, address) = server_socket.accept()
            print 'networking_thread: client connected'

            try:
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
        while True:
            eye.run()
    except BaseException as e:
        traceback.print_exc()
        print 'scanning_thread: laser down: %s' % str(e)


def main_thread(controller, driver):
    try:
        while True:
            controller.run()
            driver.run()
            time.sleep(0.1)
    except BaseException as e:
        traceback.print_exc()
        print 'main_thread: main down: %s' % str(e)


def configure_robo(laser_port, robo_port):
    laser = hokuyo.Hokuyo(laser_port)
    laser.laser_on()

    robo_front = roboclaw.Roboclaw(robo_port, FRONT_RC_ADDRESS)
    robo_rear = roboclaw.Roboclaw(robo_port, REAR_RC_ADDRESS)

    for robo in (robo_front, robo_rear):
        robo.set_m1_pidq(MOTORS_P_CONST, MOTORS_I_CONST, MOTORS_D_CONST, MOTORS_MAX_QPPS)
        robo.set_m2_pidq(MOTORS_P_CONST, MOTORS_I_CONST, MOTORS_D_CONST, MOTORS_MAX_QPPS)

    eye = agent.Eye(laser)
    driver = agent.Driver(robo_front, robo_rear)
    controller = agent.Controller(eye, driver)

    return eye, driver, controller


def main(laser_port, robo_port):
    eye, driver, controller = configure_robo(laser_port, robo_port)

    thread.start_new_thread(networking_thread, (controller, ))
    thread.start_new_thread(scanning_thread, (eye, ))

    main_thread(controller, driver)
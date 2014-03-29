import serial
import sys

from navi.driver import roboclaw
from navi.tools import serial_port


UART_PORT = "/dev/ttyO3"
UART_SPEED = 38400

REAR_RC_ADDRESS = 128
FRONT_RC_ADDRESS = 129

MOTORS_MAX_QPPS = 13800
MOTORS_P_CONST = 65536
MOTORS_I_CONST = 32768
MOTORS_D_CONST = 16384

PID_QPPS = (MOTORS_P_CONST, MOTORS_I_CONST, MOTORS_D_CONST, MOTORS_MAX_QPPS)

__author__ = 'paoolo'

if __name__ == '__main__':
    robo_serial = serial.Serial(port=UART_PORT, baudrate=UART_SPEED, timeout=0.1)
    port = serial_port.SerialPort(robo_serial)

    robo_rear = roboclaw.Roboclaw(port, REAR_RC_ADDRESS)
    robo_front = roboclaw.Roboclaw(port, FRONT_RC_ADDRESS)

    for robo in (robo_front, robo_rear):
        robo.set_m1_pidq(*PID_QPPS)
        robo.set_m2_pidq(*PID_QPPS)

    print '%d: %s' % (len(sys.argv), str(sys.argv))

    if len(sys.argv) == 3:
        left, right = int(sys.argv[1]), int(sys.argv[2])
        robo_rear.set_mixed_speed(left, right)
        robo_front.set_mixed_speed(left, right)

    elif len(sys.argv) == 2:
        speed = int(sys.argv[1])
        robo_rear.set_mixed_speed(speed, speed)
        robo_front.set_mixed_speed(speed, speed)

    else:
        robo_rear.set_mixed_speed(0, 0)
        robo_front.set_mixed_speed(0, 0)
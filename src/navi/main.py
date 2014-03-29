import serial

from tools import app
from tools import serial_port


__author__ = 'paoolo'

if __name__ == '__main__':
    laser_serial = serial.Serial(port="/dev/ttyACM0", baudrate=19200, timeout=0.1)
    robo_serial = serial.Serial(port="/dev/ttyO3", baudrate=38400, timeout=0.1)

    laser_port = serial_port.SerialPort(laser_serial)
    robo_port = serial_port.SerialPort(robo_serial)

    app.main(laser_port, robo_port)
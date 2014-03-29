import mockito

from tools import app
from tools import serial_port


__author__ = 'paoolo'

if __name__ == '__main__':
    laser_serial = mockito.mock()
    robo_serial = mockito.mock()

    laser_port = serial_port.SerialPort(laser_serial)
    robo_port = serial_port.SerialPort(robo_serial)

    app.main(laser_port, robo_port)
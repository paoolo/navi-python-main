import socket
import struct
import sys
import re

from navi.proto import controlmsg_pb2


__author__ = 'paoolo'

if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 1234))

    while True:
        sys.stdout.write('>>> ')
        cmd = sys.stdin.readline()[:-1]

        if re.match('\s*[0-9]+\s*[0-9]+\s*', cmd):
            cmd = re.sub('\s+', ' ', cmd.strip())

            values = map(lambda a: int(a), cmd.split(' '))
            msg = controlmsg_pb2.ControlMessage()
            msg.type, msg.left, msg.right = controlmsg_pb2.SET, values[0], values[1]

            data_to_send = msg.ByteSize()
            data = msg.SerializeToString()

            client_socket.send(struct.pack('H', data_to_send))
            client_socket.send(data)

            print 'sent %d %d' % (values[0], values[1])
        else:
            print 'R L'
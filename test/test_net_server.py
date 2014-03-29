import socket
import struct
import traceback

from proto import controlmsg_pb2


__author__ = 'paoolo'

if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 1234))
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

                        print '%s: (left=%d, right=%d)' % (str(msg.type), int(msg.left), int(msg.right))

                print 'networking_thread: client disconnected'

            except BaseException as e:
                traceback.print_exc()
                print 'networking_thread: client error: %s' % str(e)

    except BaseException as e:
        traceback.print_exc()
        print 'networking_thread: server down: %s' % str(e)
import sys
import time

from amber.common import amber_client
from amber.roboclaw import roboclaw


__author__ = 'paoolo'

if __name__ == '__main__':
    amber_ip = raw_input('IP (default: 127.0.0.1): ')
    amber_ip = '127.0.0.1' if amber_ip is None or len(amber_ip) == 0 else amber_ip
    client = amber_client.AmberClient(amber_ip)

    proxy = roboclaw.RoboclawProxy(client, 0)

    print '%d: %s' % (len(sys.argv), str(sys.argv))

    if len(sys.argv) == 3:
        left, right = int(sys.argv[1]), int(sys.argv[2])
        proxy.send_motors_command(left, right, left, right)

    elif len(sys.argv) == 2:
        speed = int(sys.argv[1])
        proxy.send_motors_command(speed, speed, speed, speed)

    else:
        proxy.send_motors_command(0, 0, 0, 0)

    time.sleep(10)

    client.terminate()
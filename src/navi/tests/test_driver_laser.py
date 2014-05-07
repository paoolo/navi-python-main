from amber.common import amber_client
from amber.hokuyo import hokuyo

__author__ = 'paoolo'

if __name__ == '__main__':
    amber_ip = raw_input('IP (default: 127.0.0.1): ')
    amber_ip = '127.0.0.1' if amber_ip is None or len(amber_ip) == 0 else amber_ip
    client = amber_client.AmberClient(amber_ip)

    proxy = hokuyo.HokuyoProxy(client, 0)

    print(proxy.get_version_info())
    print(proxy.get_sensor_state())
    print(proxy.get_sensor_specs())
    scan = proxy.get_single_scan()
    print(scan.get_points())

    client.terminate()
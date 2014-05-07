from navi.tools import app


__author__ = 'paoolo'

if __name__ == '__main__':
    amber_ip = raw_input('IP (default: 127.0.0.1): ')
    amber_ip = '127.0.0.1' if amber_ip is None or len(amber_ip) == 0 else amber_ip
    app.main(amber_ip)
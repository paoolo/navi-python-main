import sys
from navi.tools import app


__author__ = 'paoolo'

if __name__ == '__main__':
    amber_ip = '127.0.0.1' if len(sys.argv) < 2 else sys.argv[1]
    app.main(amber_ip)
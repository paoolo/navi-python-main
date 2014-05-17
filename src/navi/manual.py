import sys

from amber.common import runtime

from navi.tools import app


__author__ = 'paoolo'

if __name__ == '__main__':
    amber_ip = '127.0.0.1' if len(sys.argv) < 2 else sys.argv[1]
    _app = app.App(amber_ip)
    runtime.add_shutdown_hook(_app.terminate)
    _app.manual()
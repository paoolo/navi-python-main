import os
import sys

from navi.tools import app, web


__author__ = 'paoolo'

if __name__ == '__main__':
    _amber_ip = '127.0.0.1' if len(sys.argv) < 2 else sys.argv[1]

    _app = app.App(_amber_ip)

    if '_APP_BARE' not in os.environ:
        web.start(_app)

    _app.auto()
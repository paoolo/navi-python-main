import os
import sys

from navi.tools import app


__author__ = 'paoolo'

BARE = '_APP_BARE' in os.environ
if not BARE:
    from navi.tools import web

if __name__ == '__main__':
    _amber_ip = '127.0.0.1' if len(sys.argv) < 2 else sys.argv[1]

    _app = app.App(_amber_ip)

    if not BARE:
        web.start(_app)

    _app.manual()
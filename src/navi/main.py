import threading
import time

from amber.common import runtime

from navi.web.page import run_flask, stop_flask
from navi.web.push import run_tornado, stop_tornado
from navi.app.main import run_main, stop_main


_registry = dict()


def stop():
    _registry['alive'] = False


if __name__ == '__main__':
    _tornado_thread = threading.Thread(target=run_tornado, args=(_registry,))
    runtime.add_shutdown_hook(stop_tornado)
    _tornado_thread.start()

    _flask_thread = threading.Thread(target=run_flask, args=(_registry,))
    runtime.add_shutdown_hook(stop_flask)
    _flask_thread.start()

    _app_thread = threading.Thread(target=run_main, args=(_registry,))
    runtime.add_shutdown_hook(stop_main)
    _app_thread.start()

    runtime.add_shutdown_hook(stop)

    _registry['alive'] = True
    while _registry['alive']:
        time.sleep(1.0)
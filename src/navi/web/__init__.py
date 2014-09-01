import threading

from amber.common import runtime
from navi.web.page import run_flask, stop_flask
from navi.web.push import run_tornado, stop_tornado


def start(chain):
    _tornado_thread = threading.Thread(target=run_tornado, args=(chain,))
    _tornado_thread.start()
    runtime.add_shutdown_hook(stop_tornado)

    _flask_thread = threading.Thread(target=run_flask, args=(chain,))
    _flask_thread.start()
    runtime.add_shutdown_hook(stop_flask)
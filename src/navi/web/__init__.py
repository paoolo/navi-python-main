import threading

from amber.common import runtime
from navi.web.page import run_flask, stop_flask
from navi.web.push import run_tornado, stop_tornado


def start(chain):
    _tornado_thread = threading.Thread(target=run_tornado, args=(chain,))
    runtime.add_shutdown_hook(stop_tornado)
    _tornado_thread.start()

    _flask_thread = threading.Thread(target=run_flask, args=(chain,))
    runtime.add_shutdown_hook(stop_flask)
    _flask_thread.start()
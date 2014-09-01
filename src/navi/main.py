import time
import traceback
import sys

from amber.common import runtime

from amber.common.amber_client import AmberClient
from amber.hokuyo.hokuyo import HokuyoProxy
from amber.roboclaw.roboclaw import RoboclawProxy
from navi.components.chain import Chain
from navi.components.avoidance.rodeo_swap import RodeoSwap
from navi.components.control.const import Const
from navi.components.control.driver import Driver
from navi.components.control.manual import Manual
from navi.components.control.randomize import Random
from navi.components.limit.distance import Distance
from navi.components.limit.forward import Forward
from navi.components.limit.reverse import Reverse
from navi.components.other.low_pass_filter import LowPassFilter
from navi import web


__author__ = 'paoolo'


class Main(object):
    def __init__(self, chain):
        self._alive = True
        self._chain = chain

        runtime.add_shutdown_hook(self._terminate)
        self._main_loop()

    def _main_loop(self):
        try:
            while self._alive:
                self._chain.perform()
                time.sleep(0.11)

        except BaseException as e:
            traceback.print_exc()
            print 'main: exception: %s' % str(e)

        print 'main: stop'

    def _terminate(self):
        print 'terminate main'
        self._alive = False


if __name__ == '__main__':
    _amber_ip = '127.0.0.1' if len(sys.argv) < 2 else sys.argv[1]
    _amber_client = AmberClient(_amber_ip)
    _hokuyo_proxy = HokuyoProxy(_amber_client, 0)
    _roboclaw_proxy = RoboclawProxy(_amber_client, 0)

    _chain = Chain()

    _chain.append(Const())
    _chain.append(Random())
    _chain.append(Manual())
    _chain.append(LowPassFilter())

    _chain.append(RodeoSwap(_hokuyo_proxy))

    _chain.append(Reverse())
    _chain.append(Distance(_hokuyo_proxy))
    _chain.append(LowPassFilter())
    _chain.append(Forward())

    _chain.append(Driver(_roboclaw_proxy))

    web.start(_chain)

    Main(_chain)
import time
import traceback
import sys

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

if __name__ == '__main__':
    amber_ip = '127.0.0.1' if len(sys.argv) < 2 else sys.argv[1]

    amber_client = AmberClient(amber_ip)
    hokuyo = HokuyoProxy(amber_client, 0)
    roboclaw = RoboclawProxy(amber_client, 0)

    chain = Chain()

    chain.append(Const())
    chain.append(Random())
    chain.append(Manual())
    chain.append(LowPassFilter())

    chain.append(RodeoSwap(hokuyo))

    chain.append(Reverse())
    chain.append(Distance(hokuyo))
    chain.append(LowPassFilter())
    chain.append(Forward())

    chain.append(Driver(roboclaw))

    web.start(chain)

    alive = True
    try:
        while alive:
            chain.perform()
            time.sleep(0.11)
    except BaseException as e:
        traceback.print_exc()
        print 'main: exception: %s' % str(e)

    print 'main: stop'
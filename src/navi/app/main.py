import time
import traceback

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


_global = {}


def connect_amber(address):
    if 'amber_client' not in _global:
        amber_client = AmberClient(address)
        _global['amber_client'] = amber_client

        hokuyo_proxy = HokuyoProxy(amber_client, 0)
        hokuyo_proxy.subscribe(_global['rodeo_swap'])
        hokuyo_proxy.subscribe(_global['distance'])

        roboclaw_proxy = RoboclawProxy(amber_client, 0)
        _global['driver'].roboclaw = roboclaw_proxy


def disconnect_amber():
    if 'amber_client' in _global:
        _global['amber_client'].terminate()
        del _global['amber_client']

    if 'driver' in _global:
        _global['driver'].roboclaw = None


def run_main(registry):
    _global['alive'] = True
    _global['registry'] = registry

    chain = Chain()
    registry['chain'] = chain

    chain.append(Const())
    chain.append(Random())
    chain.append(Manual())

    chain.append(LowPassFilter())

    rodeo_swap = RodeoSwap()
    chain.append(rodeo_swap)
    _global['rodeo_swap'] = rodeo_swap

    chain.append(Reverse())

    distance = Distance()
    chain.append(distance)
    _global['distance'] = distance

    chain.append(LowPassFilter())

    chain.append(Forward())

    driver = Driver()
    chain.append(driver)
    _global['driver'] = driver

    try:
        while _global['alive']:
            chain.perform()
            time.sleep(0.11)

    except BaseException as e:
        traceback.print_exc()
        print 'main: exception: %s' % str(e)

    print 'main: stop'


def stop_main():
    print 'try to stop app...'
    _global['alive'] = False
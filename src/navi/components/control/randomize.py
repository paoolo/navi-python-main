import random
import threading
import time

from amber.common import runtime
from navi.components.component import Component


__author__ = 'paoolo'


class Random(Component):
    def __init__(self):
        super(Random, self).__init__()

        self._alive = True
        self._left = 0.0
        self._right = 0.0

        self._randomizing_width = 0.0
        self._randomizing_step = 0.0

        self._generator_thread = threading.Thread(target=self._generator_loop)
        runtime.add_shutdown_hook(self._terminate)
        self._generator_thread.start()

    def _generator_loop(self):
        print 'generator loop: start'

        while self._alive:
            self._randomize()
            time.sleep(3.25)

        print 'generator loop: stop'

    def _randomize(self):
        value = (int(random.random() * self._randomizing_width - self._randomizing_width / 2.0)
                 * self._randomizing_step)
        weight = random.random()

        if 0.35 < weight < 0.65:
            self._left += value
            self._right += value
        else:
            self._left += value * weight
            self._right += value * (1.0 - weight)

    def _terminate(self):
        print 'terminate randomize'

        self._alive = False

    def modify(self, left, right):
        return self._left, self._right

    @property
    def randomizing_width(self):
        return self._randomizing_width

    @randomizing_width.setter
    def randomizing_width(self, val):
        self._randomizing_width = float(val)

    @property
    def randomizing_step(self):
        return self._randomizing_step

    @randomizing_step.setter
    def randomizing_step(self, val):
        self._randomizing_step = float(val)
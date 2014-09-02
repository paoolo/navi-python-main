import time

from navi.components.component import Component


__author__ = 'paoolo'


class Driver(Component):
    """
    Used to drive.
    """

    def __init__(self):
        super(Driver, self).__init__()

        self._old_left = 0
        self._old_right = 0
        self._time_stamp = time.time()
        self.roboclaw = None

        self._change_diff_limit = 10.0

    def modify(self, left, right):
        time_stamp = time.time()

        if time_stamp - self._time_stamp > 1.7 \
                or abs(self._old_left - left) > self._change_diff_limit \
                or abs(self._old_right - right) > self._change_diff_limit:

            self._time_stamp = time.time()
            self._old_left, self._old_right = left, right

            if self.roboclaw is not None:
                self.roboclaw.send_motors_command(int(left), int(right), int(left), int(right))

        return left, right

    @property
    def change_diff_limit(self):
        return self._change_diff_limit

    @change_diff_limit.setter
    def change_diff_limit(self, val):
        self._change_diff_limit = float(val)
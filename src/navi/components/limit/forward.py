from navi.components.component import Component

__author__ = 'paoolo'


class Forward(Component):
    """
    Used to border maximum speed.
    """

    def __init__(self):
        super(Forward, self).__init__()

        self._max_speed = 700.0

    def modify(self, left, right):
        left = self._check_and_modify(left)
        right = self._check_and_modify(right)

        return left, right

    def _check_and_modify(self, value):
        return self._max_speed if value > self._max_speed \
            else -self._max_speed if value < -self._max_speed \
            else value

    @property
    def max_speed(self):
        return self._max_speed

    @max_speed.setter
    def max_speed(self, val):
        self._max_speed = float(val)
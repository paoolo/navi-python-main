from navi.components.component import Component

__author__ = 'paoolo'


class Reverse(Component):
    """
    Used if robot goes back.
    """

    def __init__(self):
        super(Reverse, self).__init__()

        self._rotating_speed = 200.0
        self._max_speed = 400.0

    def modify(self, left, right):
        if (left + right) / 2.0 < 0:

            if left < 0 and right < 0:
                left = left if left > -self._max_speed else -self._max_speed
                right = right if right > -self._max_speed else -self._max_speed

            elif left < 0 < right:
                right = right if right < self._rotating_speed else self._rotating_speed
                left = -right

            elif left > 0 > right:
                left = left if left < self._rotating_speed else self._rotating_speed
                right = -left

        return left, right

    @property
    def rotating_speed(self):
        return self._rotating_speed

    @rotating_speed.setter
    def rotating_speed(self, val):
        self._rotating_speed = float(val)

    @property
    def max_speed(self):
        return self._max_speed

    @max_speed.setter
    def max_speed(self, val):
        self._max_speed = float(val)
from navi.components.component import Component

__author__ = 'paoolo'


class LowPassFilter(Component):
    """
    Used to low pass.
    """

    def __init__(self):
        super(LowPassFilter, self).__init__()

        self._old_left = 0.0
        self._old_right = 0.0

        self._alpha = 0.0

    def modify(self, left, right):
        left = self._low_pass_filter(left, self._old_left)
        right = self._low_pass_filter(right, self._old_right)

        self._old_left, self._old_right = left, right

        return left, right

    def _low_pass_filter(self, new_value, old_value):
        if old_value is None:
            return new_value
        return old_value + self._alpha * (new_value - old_value)

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, val):
        self._alpha = float(val)
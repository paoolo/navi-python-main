from navi.components.component import Component

__author__ = 'paoolo'


class Const(Component):
    """
    Used to randomizing values.
    """

    def __init__(self):
        super(Const, self).__init__(enable=False)

        self._left = 200.0
        self._right = 200.0

    def modify(self, left, right):
        return self._left, self._right

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, val):
        self._left = float(val)

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, val):
        self._right = float(val)
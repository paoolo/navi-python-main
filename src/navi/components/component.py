__author__ = 'paoolo'


class Component(object):
    def __init__(self):
        self._name = self.__class__.__name__
        self._index = 0
        self._enable = True

    def modify(self, left, right):
        return left, right

    @property
    def name(self):
        return self._name

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, val):
        self._index = int(val)

    @property
    def key(self):
        return '%s%d' % (self._name, self._index)

    @property
    def enable(self):
        return self._enable

    @enable.setter
    def enable(self, val):
        self._enable = (val == 'true')

    def properties(self):
        class_items = self.__class__.__dict__.iteritems()
        return dict((k, getattr(self, k))
                    for k, v in class_items
                    if isinstance(v, property))
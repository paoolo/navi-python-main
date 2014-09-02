from navi.web import push

__author__ = 'paoolo'


class Chain(list):
    def __init__(self, seq=()):
        super(Chain, self).__init__(seq)
        self._index = 0

    def perform(self):
        left, right = 0.0, 0.0
        for component in self:
            if component.enable:
                left, right = component.modify(left, right)
                push.emit({'target': component.key,
                           'data': '%s(%d, %d)' % (component.key, left, right),
                           'x': int(left), 'y': int(right)})

    def append(self, p_object):
        p_object.index = self._index
        self._index += 1
        super(Chain, self).append(p_object)
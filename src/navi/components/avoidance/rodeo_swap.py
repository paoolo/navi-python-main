import time
import math

from amber.tests.hokuyo_example import HokuyoListener
from navi.tools import logic
from navi.components.component import Component


__author__ = 'paoolo'


class RodeoSwap(Component, HokuyoListener):
    """
    Used to change values to avoid something.
    """

    def __init__(self):
        super(RodeoSwap, self).__init__(enable=False)

        self._old_angle = 0.0
        self._scan = None

        self._handle_time_stamp = None
        self._time_stamp = time.time()

        self._robo_width = 290.0

        self._max_rotating_speed = 300.0
        self._max_speed = 700.0

        self._hard_limit = 300.0
        self._soft_limit = 700.0

        self._angle_range = math.radians(24.0)
        self._scanner_dist_offset = 10.0

        self._alpha = 1.5
        self._beta = 0.75

    def handle(self, scan):
        self._scan = scan
        self._handle_time_stamp = time.time()

    def modify(self, left, right):
        handle_time_stamp = self._handle_time_stamp

        if handle_time_stamp is None or time.time() - handle_time_stamp > 0.8:
            scan = None
        else:
            scan = self._scan

        _time_stamp = time.time()
        _delta_time = _time_stamp - self._time_stamp
        self._time_stamp = _time_stamp

        if scan is not None:
            current_angle = logic.get_angle(left, right, self._robo_width)
            current_speed = logic.get_speed(left, right)

            min_distance, min_distance_angle = logic.get_min_distance(scan, current_angle,
                                                                      self._scanner_dist_offset, self._angle_range)
            max_distance, max_distance_angle = logic.get_max_distance(scan, current_angle,
                                                                      self._scanner_dist_offset, self._angle_range)
            # print 'rodeo-swap  : min: %d, %d; max: %d, %d' % (min_distance, math.degrees(min_distance_angle),
            #                                                  max_distance, math.degrees(max_distance_angle))

            if min_distance is not None:
                soft_limit = logic.get_soft_limit(current_speed, self._max_speed,
                                                  self._soft_limit, self._hard_limit, self._alpha)
                if min_distance < soft_limit:
                    if max_distance_angle > current_angle or min_distance_angle < current_angle:
                        if left > 0:
                            max_speed = logic.get_max_speed(min_distance, soft_limit,
                                                            self._hard_limit, self._max_rotating_speed)
                            left = left if left < max_speed else max_speed
                            right = -left  # FIXME(paoolo)
                        else:
                            if right > 0:
                                _t = left
                                left = right
                                right = _t
                    elif max_distance_angle < current_angle or min_distance_angle > current_angle:
                        if right > 0:
                            max_speed = logic.get_max_speed(min_distance, soft_limit,
                                                            self._hard_limit, self._max_rotating_speed)
                            right = right if right < max_speed else max_speed
                            left = -right  # FIXME(paoolo)
                        else:
                            if left > 0:
                                _t = right
                                right = left
                                left = _t

                elif min_distance < soft_limit * self._beta:
                    left = -left
                    right = -right
        else:
            print 'rodeo-swap: no scan!'
            left, right = 0.0, 0.0

        return left, right

    @property
    def max_rotating_speed(self):
        return self._max_rotating_speed

    @max_rotating_speed.setter
    def max_rotating_speed(self, val):
        self._max_rotating_speed = float(val)

    @property
    def robo_width(self):
        return self._robo_width

    @robo_width.setter
    def robo_width(self, val):
        self._robo_width = float(val)

    @property
    def max_speed(self):
        return self._max_speed

    @max_speed.setter
    def max_speed(self, val):
        self._max_speed = float(val)

    @property
    def hard_limit(self):
        return self._hard_limit

    @hard_limit.setter
    def hard_limit(self, val):
        self._hard_limit = float(val)

    @property
    def soft_limit(self):
        return self._soft_limit

    @soft_limit.setter
    def soft_limit(self, val):
        self._soft_limit = float(val)

    @property
    def angle_range(self):
        return math.degrees(self._angle_range)

    @angle_range.setter
    def angle_range(self, val):
        self._angle_range = math.radians(float(val))

    @property
    def scanner_dist_offset(self):
        return self._scanner_dist_offset

    @scanner_dist_offset.setter
    def scanner_dist_offset(self, val):
        self._scanner_dist_offset = float(val)

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, val):
        self._alpha = float(val)

    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, val):
        self._beta = float(val)
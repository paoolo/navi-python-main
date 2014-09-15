import math
import time

from navi.components.component import Component
from navi.tools import logic


__author__ = 'paoolo'


class DriveToPoint(Component):
    def __init__(self):
        super(DriveToPoint, self).__init__(enable=False)

        self.roboclaw = None

        self._x, self._y, self._robo_angle = 0.0, 0.0, 0.0
        self._target_x, self._target_y = 0.0, 0.0

        self._robo_width = 280.0

        self._alpha = 1.0
        self._target_radius = 75.0

        self._time_stamp = time.time()
        self._active = True

    @staticmethod
    def _normalize_angle(angle):
        if angle < -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle

    def _compute_new_relative_position(self, speed_left, speed_right, delta_time):
        if speed_right == speed_left:
            _x = self._x + speed_left * delta_time * math.cos(self._robo_angle)
            _y = self._y + speed_right * delta_time * math.sin(self._robo_angle)

            _robo_angle = self._robo_angle

        else:
            _a = 0.5 * self._robo_width * (speed_right + speed_left) / (speed_right - speed_left)
            _robo_angle = self._robo_angle + (speed_right - speed_left) / self._robo_width * delta_time

            _x = self._x + _a * (math.sin(_robo_angle) - math.sin(self._robo_angle))
            _y = self._y - _a * (math.cos(_robo_angle) - math.cos(self._robo_angle))

            _robo_angle = DriveToPoint._normalize_angle(_robo_angle)

        return _x, _y, _robo_angle

    def modify(self, left, right):
        if abs(self._x - self._target_x) < self._target_radius \
                and abs(self._y - self._target_y) < self._target_radius:
            return 0.0, 0.0

        if self.roboclaw is None:
            return left, right

        _speed = self.roboclaw.get_current_motors_speed()
        _speed_left, speed_right = _speed.get_front_left_speed(), _speed.get_front_right_speed()

        if abs(_speed_left - left) > 500.0 or abs(speed_right - right) > 500.0:
            return left, right

        _time_stamp = time.time()
        _delta_time = _time_stamp - self._time_stamp
        self._time_stamp = _time_stamp

        self._x, self._y, self._robo_angle = self._compute_new_relative_position(_speed_left, speed_right, _delta_time)

        _target_angle = math.atan2(self._target_y - self._y, self._target_x - self._x)

        _drive_angle = _target_angle - self._robo_angle
        _drive_angle = DriveToPoint._normalize_angle(_drive_angle)

        if not self._active:
            self._active = (abs(_drive_angle) > 2.0 * math.pi / 3.0)
        else:
            self._active = not (abs(_drive_angle) < 0.03490658503988659)

        print 'drive_to_point: %s, %f, %f, %f, %f, %f, %f' % (str(self._active),
                                                              math.degrees(_target_angle),
                                                              math.degrees(self._robo_angle),
                                                              math.degrees(_drive_angle),
                                                              _drive_angle / math.pi,
                                                              self._x, self._y)

        if not self._active:
            return left, right

        else:
            _drive_speed = logic.get_speed(left, right)

            return _drive_speed - self._alpha * _drive_angle / math.pi * _drive_speed, \
                   _drive_speed + self._alpha * _drive_angle / math.pi * _drive_speed

    @property
    def target_x(self):
        return self._target_x

    @target_x.setter
    def target_x(self, val):
        self._target_x = float(val)

    @property
    def target_y(self):
        return self._target_y

    @target_y.setter
    def target_y(self, val):
        self._target_y = float(val)

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, val):
        self._alpha = float(val)

    @property
    def target_radius(self):
        return self._target_radius

    @target_radius.setter
    def target_radius(self, val):
        self._target_radius = float(val)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        pass

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        pass

    @property
    def robo_angle(self):
        return math.degrees(self._robo_angle)

    @robo_angle.setter
    def robo_angle(self, val):
        pass
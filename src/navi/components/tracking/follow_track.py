from navi.components.component import Component

__author__ = 'paoolo'


class FollowTrack(Component):
    def __init__(self, roboclaw):
        super(FollowTrack, self).__init__(enable=False)

        self._val_p = 0.0
        self._val_i = 0.0
        self._val_d = 0.0
        self._previous_error = 0.0
        self._roboclaw = roboclaw

        self._param_p = 0.7
        self._param_i = 0.5
        self._param_d = 0.2

    def modify(self, left, right):
        motor_speed = self._roboclaw.get_current_motors_speed()
        read_left = (motor_speed.get_front_left_speed() + motor_speed.get_rear_left_speed()) / 2.0
        read_right = (motor_speed.get_front_right_speed() + motor_speed.get_rear_right_speed()) / 2.0
        error = left - read_left + right - read_right
        self._val_p *= self._param_p
        self._val_i += error
        self._val_i *= self._param_i
        self._val_d = error - self._previous_error
        self._previous_error = error
        correction = self._val_p + self._val_i + self._val_d
        return left - correction, right + correction

    @property
    def param_p(self):
        return self._param_p

    @param_p.setter
    def param_p(self, val):
        self._param_p = float(val)

    @property
    def param_i(self):
        return self._param_i

    @param_i.setter
    def param_i(self, val):
        self._param_i = float(val)

    @property
    def param_d(self):
        return self._param_d

    @param_d.setter
    def param_d(self, val):
        self._param_d = float(val)
import abc
import random

from navi.tools import logic, config, web


__author__ = 'paoolo'


class Chain(list):
    def __init__(self, seq=()):
        super(Chain, self).__init__(seq)

    def perform(self):
        left, right = 0.0, 0.0
        for component in self:
            left, right = component.modify(left, right)

    def reload(self):
        for component in self:
            component.reload()


class Component(object):
    def modify(self, left, right):
        return left, right

    @abc.abstractmethod
    def reload(self):
        pass


class Manual(Component):
    """
    Used to manual.
    """

    def __init__(self):
        self.__left, self.__right = 0, 0

    def set(self, left, right):
        self.__left, self.__right = left, right

    def change(self, left, right):
        self.__left += left
        self.__right += right

    def modify(self, left, right):
        web.emit({'target': 'manual',
                  'data': 'manual(%d, %d)' % (self.__left, self.__right),
                  'x': int(left), 'y': int(right)})
        return self.__left, self.__right

    def reload(self):
        pass


class Randomize(Component):
    """
    Used to randomizing values.
    """

    def __init__(self):
        self.__left, self.__right = 0.0, 0.0
        self.__randomizing_width, self.__randomizing_step = 0.0, 0.0
        self.__rotating_speed = 0.0
        self.reload()

    def randomize(self):
        value = (int(random.random() * self.__randomizing_width - self.__randomizing_width / 2.0)
                 * self.__randomizing_step)
        weight = random.random()

        if 0.35 < weight < 0.65:
            self.__left += value
            self.__right += value
        else:
            self.__left += value * weight
            self.__right += value * (1.0 - weight)

        left, right = self.__left, self.__right

        if (left + right) / 2.0 < 0:
            if left < 0 and right < 0:
                left, right = 0.0, 0.0

            elif left < 0 < right:
                right = right if right < self.__rotating_speed else self.__rotating_speed
                left = -right

            elif left > 0 > right:
                left = left if left < self.__rotating_speed else self.__rotating_speed
                right = -left

        self.__left, self.__right = left, right

    def modify(self, left, right):
        web.emit({'target': 'randomize',
                  'data': 'randomize(%d, %d)' % (self.__left, self.__right),
                  'x': int(self.__left), 'y': int(self.__right)})
        return self.__left, self.__right

    def reload(self):
        self.__randomizing_width = float(config.RANDOMIZING_WIDTH)
        self.__randomizing_step = float(config.RANDOMIZING_STEP)
        self.__rotating_speed = float(config.BACK_ROTATING_SPEED)


class RodeoSwap(Component):
    """
    Used to change values to avoid something.
    """

    def __init__(self):
        self.__scan = None
        self.__rotating_speed, self.__robo_width, self.__hard_limit = 0.0, 0.0, 0.0
        self.reload()

    def handle(self, scan):
        self.__scan = scan

    def modify(self, left, right):
        scan = self.__scan

        if scan is not None:
            current_angle = logic.get_angle(left, right, self.__robo_width)
            min_distance, min_distance_angle = logic.get_min_distance(scan, current_angle)

            if min_distance is not None:
                # FIXME(paoolo) 2.2 as config param
                if min_distance < self.__hard_limit * 1.7:
                    if min_distance_angle < current_angle:
                        if left > 0:
                            left = left if left < self.__rotating_speed else self.__rotating_speed
                            right = -left  # FIXME(paoolo)
                        else:
                            if right > 0:
                                _t = left
                                left = right
                                right = _t
                    else:
                        if right > 0:
                            right = right if right < self.__rotating_speed else self.__rotating_speed
                            left = -right  # FIXME(paoolo)
                        else:
                            if left > 0:
                                _t = right
                                _t = right
                                right = left
                                left = _t

                # FIXME(paoolo) 1.1 as config param
                elif min_distance < self.__hard_limit * 1.2:
                    left = -left
                    right = -right
        else:
            print 'no scan!'
            left, right = 0.0, 0.0

        web.emit({'target': 'rodeo_swap',
                  'data': 'rodeo_swap(%d, %d)' % (left, right),
                  'x': int(left), 'y': int(right)})
        return left, right

    def reload(self):
        self.__rotating_speed = float(config.RODEO_SWAP_ROTATING_SPEED)
        self.__robo_width = float(config.ROBO_WIDTH)
        self.__hard_limit = float(config.HARD_LIMIT)


class LowPassFilter(Component):
    """
    Used to low pass.
    """

    def __init__(self):
        self.__old_left, self.__old_right = 0, 0
        self.__low_pass_alpha = 0.0
        self.reload()

    def modify(self, left, right):
        left = self.__low_pass_filter(left, self.__old_left)
        right = self.__low_pass_filter(right, self.__old_right)
        self.__old_left, self.__old_right = left, right
        return left, right

    def __low_pass_filter(self, new_value, old_value):
        if old_value is None:
            return new_value
        return old_value + self.__low_pass_alpha * (new_value - old_value)

    def reload(self):
        self.__low_pass_alpha = float(config.LOW_PASS_ALPHA)


class Back(Component):
    """
    Used if robot goes back.
    """

    def __init__(self):
        self.__rotating_speed = 0.0
        self.reload()

    def modify(self, left, right):
        if (left + right) / 2.0 < 0:

            if left < 0 and right < 0:
                left, right = 0.0, 0.0

            elif left < 0 < right:
                right = right if right < self.__rotating_speed else self.__rotating_speed
                left = -right

            elif left > 0 > right:
                left = left if left < self.__rotating_speed else self.__rotating_speed
                right = -left

        web.emit({'target': 'back',
                  'data': 'back(%d, %d)' % (left, right),
                  'x': int(left), 'y': int(right)})
        return left, right

    def reload(self):
        self.__rotating_speed = float(config.BACK_ROTATING_SPEED)


class Controller(Component):
    """
    Used to control speed.
    """

    def __init__(self):
        self.__scan = None
        self.__max_speed, self.__robo_width = 0.0, 0.0
        self.__hard_limit, self.__soft_limit = 0.0, 0.0
        self.reload()

    def handle(self, scan):
        self.__scan = scan

    def modify(self, left, right):
        if left > 0 or right > 0:
            current_angle = logic.get_angle(left, right, self.__robo_width)
            scan = self.__scan

            if scan is not None:
                min_distance, _ = logic.get_min_distance(scan, current_angle)
                if min_distance is not None:

                    if self.__hard_limit < min_distance < self.__soft_limit:
                        current_speed = (left + right) / 2.0
                        max_speed = self.__get_max_speed(min_distance)

                        if current_speed > max_speed:
                            divide = max_speed / current_speed
                            left = left * divide
                            right = right * divide

                    elif min_distance <= self.__hard_limit:
                        left, right = 0, 0

            else:
                left, right = 0.0, 0.0

        web.emit({'target': 'controller',
                  'data': 'controller(%d, %d)' % (left, right),
                  'x': int(left), 'y': int(right)})
        return left, right

    def __get_max_speed(self, distance):
        return self.__max_speed / (self.__soft_limit - self.__hard_limit) * float(distance) - \
               (self.__max_speed * self.__hard_limit) / (self.__soft_limit - self.__hard_limit)

    def reload(self):
        self.__max_speed = float(config.MAX_SPEED)
        self.__robo_width = float(config.ROBO_WIDTH)
        self.__hard_limit = float(config.HARD_LIMIT)
        self.__soft_limit = float(config.SOFT_LIMIT)


class Stop(Component):
    """
    Used to border maximum speed.
    """

    def __init__(self):
        self.__max_speed = 0.0
        self.reload()

    def modify(self, left, right):
        left, right = self.__check(left), self.__check(right)
        web.emit({'target': 'stop',
                  'data': 'stop(%d, %d)' % (left, right),
                  'x': int(left), 'y': int(right)})
        return left, right

    def __check(self, value):
        return self.__max_speed if value > self.__max_speed \
            else -self.__max_speed if value < -self.__max_speed \
            else value

    def reload(self):
        self.__max_speed = float(config.MAX_SPEED)


class PID(Component):
    """
    Used to PID.
    """

    P, I, D = 0, 0, 0

    def __init__(self, engine):
        self.__engine = engine
        self.__previous_error, self.__integral = 0.0, 0.0
        self.__alpha = 0.0
        self.reload()

    def modify(self, left, right):
        # FIXME(paoolo) asynchronous this
        # FIXME(paoolo) check if value is ok?
        current_speed = self.__engine.get_current_motors_speed()

        front_left = current_speed.get_front_left_speed()
        rear_left = current_speed.get_rear_left_speed()

        front_right = current_speed.get_front_right_speed()
        rear_right = current_speed.get_rear_right_speed()

        current_left = (front_left + rear_left) / 2.0
        current_right = (front_right + rear_right) / 2.0

        left = left - (current_left - left) * self.__alpha
        right = right - (current_right - right) * self.__alpha

        web.emit({'target': 'pid',
                  'data': 'pid(%d, %d)' % (left, right),
                  'x': int(left), 'y': int(right)})

        return left, right

    def __pid(self, set_point=None, measured_value=None, dt=None):
        error = set_point - measured_value
        self.__integral += error * dt
        derivative = (error - self.__previous_error) / dt
        output = PID.P * error + PID.I * self.__integral + PID.D * derivative
        self.__previous_error = error
        # wait(dt)

    def reload(self):
        self.__alpha = float(config.PID_ALPHA)


class Driver(Component):
    """
    Used to drive.
    """

    def __init__(self, engine):
        self.__engine = engine
        self.__old_left, self.__old_right = 0, 0
        self.__change_diff_limit = 0.0
        self.reload()

    def modify(self, left, right):
        if abs(self.__old_left - left) > self.__change_diff_limit \
            or abs(self.__old_right - right) > self.__change_diff_limit:
            self.__old_left, self.__old_right = left, right
            self.__engine.send_motors_command(int(left), int(right), int(left), int(right))

        web.emit({'target': 'driver',
                  'data': 'driver(%d, %d)' % (left, right),
                  'x': int(left), 'y': int(right)})
        return left, right

    def reload(self):
        self.__change_diff_limit = float(config.CHANGE_DIFF_LIMIT)
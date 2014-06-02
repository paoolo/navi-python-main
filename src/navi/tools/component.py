import random

from navi.tools import logic, config


__author__ = 'paoolo'


class Chain(list):
    def __init__(self, seq=()):
        super(Chain, self).__init__(seq)

    def perform(self):
        left, right = 0.0, 0.0
        for component in self:
            left, right = component.modify(left, right)


class Component(object):
    def modify(self, left, right):
        return left, right


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
        print 'manual(%d, %d)' % (self.__left, self.__right)
        return self.__left, self.__right


class Randomize(Component):
    """
    Used to randomizing values.
    """

    RANDOMIZING_WIDTH = float(config.RANDOMIZING_WIDTH)
    RANDOMIZING_STEP = float(config.RANDOMIZING_STEP)

    def __init__(self):
        self.__left, self.__right = 0.0, 0.0

    def modify(self, left, right):
        self.__left += (Randomize.__randomize() * Randomize.RANDOMIZING_STEP)
        self.__right += (Randomize.__randomize() * Randomize.RANDOMIZING_STEP)

        print 'randomize(%d, %d)' % (self.__left, self.__right)
        return self.__left, self.__right

    @staticmethod
    def __randomize():
        return int(random.random() * Randomize.RANDOMIZING_WIDTH - Randomize.RANDOMIZING_WIDTH / 2.0)


class RodeoSwap(Component):
    """
    Used to change values to avoid something.
    """

    ROTATING_SPEED = float(config.RODEO_SWAP_ROTATING_SPEED)
    ROBO_WIDTH = float(config.ROBO_WIDTH)
    HARD_LIMIT = float(config.HARD_LIMIT)

    def __init__(self):
        self.__scan = None

    def modify(self, left, right):
        scan = self.__scan

        if scan is not None:
            current_angle = logic.get_angle(left, right, RodeoSwap.ROBO_WIDTH)
            min_distance, min_distance_angle = logic.get_min_distance(scan, current_angle)

            if min_distance is not None:
                if min_distance < RodeoSwap.HARD_LIMIT * 2.2:
                    if min_distance_angle < current_angle:
                        # go to right
                        if left > 0:
                            print '>> Rodeo to right'
                            left = left if left < RodeoSwap.ROTATING_SPEED else RodeoSwap.ROTATING_SPEED
                            right = -left  # FIXME(paoolo)
                        else:
                            if right > 0:
                                print '>> Swap to right'
                                _t = left
                                left = right
                                right = _t
                    else:
                        # go to left
                        if right > 0:
                            print '>> Rodeo to left'
                            right = right if right < RodeoSwap.ROTATING_SPEED else RodeoSwap.ROTATING_SPEED
                            left = -right  # FIXME(paoolo)
                        else:
                            if left > 0:
                                print '>> Swap to left'
                                _t = right
                                right = left
                                left = _t

                elif min_distance < RodeoSwap.HARD_LIMIT * 1.1:
                    left = -left
                    right = -right
        else:
            left, right = 0.0, 0.0

        print 'rodeo_swap(%d, %d)' % (left, right)
        return left, right

    def handle(self, scan):
        self.__scan = scan


class Back(Component):
    """
    Used if robot goes back.
    """

    ROTATING_SPEED = float(config.BACK_ROTATING_SPEED)

    def modify(self, left, right):
        if (left + right) / 2.0 < 0:

            if left < 0 and right < 0:
                left, right = 0.0, 0.0

            elif left < 0 < right:
                right = right if right < Back.ROTATING_SPEED else Back.ROTATING_SPEED
                left = -right

            elif left > 0 > right:
                left = left if left < Back.ROTATING_SPEED else Back.ROTATING_SPEED
                right = -left

        print 'back(%d, %d)' % (left, right)
        return left, right


class Controller(Component):
    """
    Used to control speed.
    """

    ROBO_WIDTH = float(config.ROBO_WIDTH)
    HARD_LIMIT = float(config.HARD_LIMIT)
    SOFT_LIMIT = float(config.SOFT_LIMIT)

    def __init__(self):
        self.__scan = None

    def modify(self, left, right):
        if left > 0 or right > 0:
            current_angle = logic.get_angle(left, right, Controller.ROBO_WIDTH)
            scan = self.__scan

            if scan is not None:
                min_distance, _ = logic.get_min_distance(scan, current_angle)
                if min_distance is not None:

                    if Controller.HARD_LIMIT < min_distance < Controller.SOFT_LIMIT:
                        current_speed = (left + right) / 2.0
                        max_speed = logic.get_max_speed(min_distance)

                        if current_speed > max_speed:
                            divide = max_speed / current_speed
                            left = left * divide
                            right = right * divide

                    elif min_distance <= Controller.HARD_LIMIT:
                        left, right = 0, 0

            else:
                left, right = 0.0, 0.0

        print 'controller(%d, %d)' % (left, right)
        return left, right

    def handle(self, scan):
        self.__scan = scan


class Stop(Component):
    """
    Used to border maximum speed.
    """

    MAX_SPEED = float(config.MAX_SPEED)

    def modify(self, left, right):
        left, right = Stop.__check(left), Stop.__check(right)
        print 'stop(%d, %d)' % (left, right)
        return left, right

    @staticmethod
    def __check(value):
        return Stop.MAX_SPEED if value > Stop.MAX_SPEED \
            else -Stop.MAX_SPEED if value < -Stop.MAX_SPEED \
            else value


class Driver(Component):
    """
    Used to drive.
    """

    LOW_PASS_ALPHA = float(config.LOW_PASS_ALPHA)
    CHANGE_DIFF_LIMIT = float(config.CHANGE_DIFF_LIMIT)

    def __init__(self, engine):
        self.__engine = engine
        self.__old_left, self.__old_right = 0, 0

    def modify(self, left, right):
        if abs(self.__old_left - left) > Driver.CHANGE_DIFF_LIMIT \
                or abs(self.__old_right - right) > Driver.CHANGE_DIFF_LIMIT:
            left = Driver.__low_pass_filter(left, self.__old_left)
            right = Driver.__low_pass_filter(right, self.__old_right)

            self.__old_left, self.__old_right = left, right

            self.__engine.send_motors_command(int(left), int(right), int(left), int(right))

        print 'driver(%d, %d)' % (left, right)
        return left, right

    @staticmethod
    def __low_pass_filter(new_value, old_value):
        if old_value is None:
            return new_value
        return old_value + Driver.LOW_PASS_ALPHA * (new_value - old_value)
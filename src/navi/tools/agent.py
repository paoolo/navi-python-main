import random

from navi.tools import logic, config


__author__ = 'paoolo'


class Eye(object):
    def __init__(self, laser):
        self.__laser, self.__scan = laser, None
        self.__laser.subscribe(self)

    def get(self):
        return self.__scan

    def handle(self, scan):
        self.__scan = scan


MAX_SPEED = float(config.MAX_SPEED)
LOW_PASS_ALPHA = float(config.LOW_PASS_ALPHA)


class Driver(object):
    def __init__(self, robo):
        self.__robo = robo
        self.__old_left, self.__old_right = 0, 0
        self.__left, self.__right = 0, 0

    def set(self, left, right):
        self.__left, self.__right = left, right

    def set_circular(self, radius, linear_speed, angular_speed):
        left, right = logic.calculate(radius, linear_speed, angular_speed)
        self.__left, self.__right = left, right

    def change(self, left, right):
        self.__left += left
        self.__right += right

    def change_circular(self, radius, linear_speed, angular_speed):
        left, right = logic.calculate(radius, linear_speed, angular_speed)
        self.__left += left
        self.__right += right

    def run(self):
        if abs(self.__old_left - self.__left) > 10 or abs(self.__old_right - self.__right) > 10:
            self.__left = Driver.__low_pass_filter(self.__left, self.__old_left)
            self.__right = Driver.__low_pass_filter(self.__right, self.__old_right)

            self.__old_left, self.__old_right = self.__left, self.__right

            self.__left = MAX_SPEED if self.__left > MAX_SPEED else \
                -MAX_SPEED if self.__left < -MAX_SPEED else self.__left
            self.__right = MAX_SPEED if self.__right > MAX_SPEED else \
                -MAX_SPEED if self.__right < -MAX_SPEED else self.__right

            self.__robo.send_motors_command(int(self.__left), int(self.__right), int(self.__left), int(self.__right))
        print 'drive: %d, %d' % (self.__left, self.__right)

    @staticmethod
    def __low_pass_filter(new_value, old_value):
        if old_value is None:
            return new_value
        return old_value + LOW_PASS_ALPHA * (new_value - old_value)


SCANNER_DIST_OFFSET = float(config.SCANNER_DIST_OFFSET)

ANGLE_RANGE = float(config.ANGLE_RANGE)

SOFT_LIMIT = float(config.SOFT_LIMIT)
HARD_LIMIT = float(config.HARD_LIMIT)


def get_min_distance(scan, current_angle):
    scan = scan.get_points()
    min_distance = None
    min_distance_angle = None

    for angle, distance in scan.items():
        if distance > SCANNER_DIST_OFFSET and current_angle - ANGLE_RANGE < angle < current_angle + ANGLE_RANGE:
            if min_distance is None or distance < min_distance:
                min_distance = distance
                min_distance_angle = angle

    return min_distance, min_distance_angle


ROBO_WIDTH = float(config.ROBO_WIDTH)


class Controller(object):
    def __init__(self, eye, driver):
        self.__eye, self.__driver = eye, driver
        self.__left, self.__right = 0, 0

    def set(self, left, right):
        self.__left, self.__right = left, right

    def change(self, left, right):
        print 'change: %d, %d' % (left, right)
        self.__left += left
        self.__right += right

    def run(self):
        left, right = self.__left, self.__right

        if left > 0 or right > 0:
            current_angle = logic.get_angle(left, right, ROBO_WIDTH)
            print 'cur angle: %d' % current_angle

            scan = self.__eye.get()
            if scan is not None:
                min_distance, _ = get_min_distance(scan, current_angle)
                if min_distance is not None:
                    if HARD_LIMIT < min_distance < SOFT_LIMIT:
                        current_speed = (left + right) / 2.0
                        max_speed = logic.get_max_speed(min_distance)

                        if current_speed > max_speed:
                            divide = max_speed / current_speed
                            left = left * divide
                            right = right * divide

                    elif min_distance <= HARD_LIMIT:
                        left, right = 0, 0

                    print 'distance: %d' % min_distance
            else:
                print 'no scan!'
                left, right = 0.0, 0.0

        self.__driver.set(left, right)


class Randomize(object):
    def __init__(self, eye, controller, randomizing_width=4.0):
        self.__eye, self.__controller = eye, controller
        self.__randomizing_width = randomizing_width
        self.__left, self.__right = 0.0, 0.0

    def __randomize(self):
        return int(random.random() * self.__randomizing_width - self.__randomizing_width / 2.0)

    def run(self):
        self.__left += (self.__randomize() * 25)
        self.__right += (self.__randomize() * 25)

        self.__left = self.__left if self.__left < MAX_SPEED else MAX_SPEED
        self.__right = self.__right if self.__right < MAX_SPEED else MAX_SPEED

        left, right = self.__left, self.__right

        current_angle = logic.get_angle(left, right, ROBO_WIDTH)

        scan = self.__eye.get()

        if scan is not None:
            min_distance, min_distance_angle = get_min_distance(scan, current_angle)
            if min_distance is not None:
                if min_distance < HARD_LIMIT * 2.2:
                    if min_distance_angle < current_angle:
                        # go to right
                        if left > 0:
                            print '>> Rodeo to right'
                            left = left if left < 300.0 else 300.0
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
                            right = right if right < 300.0 else 300.0
                            left = -right  # FIXME(paoolo)
                        else:
                            if left > 0:
                                print '>> Swap to left'
                                _t = right
                                right = left
                                left = _t

                    if (left + right) / 2.0 < 0:
                        if left < 0 and right < 0:
                            left, right = 0.0, 0.0
                        elif left < 0 < right:
                            right = right if right < 200.0 else 200.0
                            left = -right
                        elif left > 0 > right:
                            left = left if left < 200.0 else 200.0
                            right = -left

                elif min_distance < HARD_LIMIT * 1.1:
                    left = -left
                    right = -right
        else:
            left, right = 0.0, 0.0

        self.__controller.set(left, right)
        print 'set controller: %d, %d' % (left, right)

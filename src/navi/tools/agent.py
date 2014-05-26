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
            self.__old_left, self.__old_right = self.__left, self.__right

            self.__left = MAX_SPEED if self.__left > MAX_SPEED else \
                -MAX_SPEED if self.__left < -MAX_SPEED else self.__left
            self.__right = MAX_SPEED if self.__right > MAX_SPEED else \
                -MAX_SPEED if self.__right < -MAX_SPEED else self.__right

            self.__robo.send_motors_command(int(self.__left), int(self.__right), int(self.__left), int(self.__right))
        print 'drive: %d, %d' % (self.__left, self.__right)


MIN_SCANNER_RANGE = float(config.MIN_SCANNER_RANGE)
ANGLE_RANGE = float(config.ANGLE_RANGE)
STOP_DIST = float(config.STOP_DIST)
LIMIT_DIST = float(config.LIMIT_DIST)


def get_min_distance(scan, current_angle):
    scan = scan.get_points()
    min_distance = None

    for angle, distance in scan.items():
        if distance > MIN_SCANNER_RANGE and current_angle - ANGLE_RANGE < angle < current_angle + ANGLE_RANGE:
            if min_distance is None or distance < min_distance:
                min_distance = distance

    return min_distance


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
                min_distance = get_min_distance(scan, current_angle)

                if STOP_DIST < min_distance < LIMIT_DIST:
                    current_speed = (left + right) / 2.0
                    max_speed = logic.get_max_speed(min_distance)

                    if current_speed > max_speed:
                        divide = max_speed / current_speed
                        left = left * divide
                        right = right * divide

                elif min_distance <= STOP_DIST:
                    left, right = 0, 0

                print 'distance: %d' % min_distance
            else:
                print 'no scan!'
                left, right = 0.0, 0.0

        self.__driver.set(left, right)


class Randomize(object):
    def __init__(self, eye, controller, randomizing_width=10.0):
        self.__eye, self.__controller = eye, controller
        self.__randomizing_width = randomizing_width
        self.__left, self.__right = 0.0, 0.0

    def __randomize(self):
        return random.random() * self.__randomizing_width - self.__randomizing_width / 2.0

    def run(self):
        self.__left += (self.__randomize() * 20)
        self.__right += (self.__randomize() * 20)

        current_angle = logic.get_angle(self.__left, self.__right, ROBO_WIDTH)

        scan = self.__eye.get()

        if scan is not None:
            min_distance = get_min_distance(scan, current_angle)

            if min_distance < STOP_DIST * 2.0:
                if random.random() < 0.5:
                    self.__left = -self.__right
                else:
                    self.__right = -self.__left
            else:
                if random.random() < 0.5:
                    self.__left = self.__right
                else:
                    self.__right = self.__left
        else:
            self.__left, self.__right = 0.0, 0.0

        if (self.__left + self.__right) / 2.0 < 0:
            if self.__left < 0 and self.__right < 0:
                self.__left, self__right = 0.0, 0.0

            elif self.__left < 0:
                self.__left = -self.__right

            elif self.__right < 0:
                self.__right = -self.__left

        self.__controller.set(self.__left, self.__right)

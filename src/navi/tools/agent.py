import random

from navi.tools.logic import calculate, get_angle


__author__ = 'paoolo'


class Eye(object):
    def __init__(self, laser):
        self.__laser, self.__scan = laser, None
        self.__laser.subscribe(self)

    def get(self):
        return self.__scan

    def handle(self, scan):
        self.__scan = scan


MAX_SPEED = 700.0
STOP_DIST = 300.0
LIMIT_DIST = 1200.0


def get_max_speed(distance):
    return MAX_SPEED / (LIMIT_DIST - STOP_DIST) * float(distance) - (MAX_SPEED * STOP_DIST) / (LIMIT_DIST - STOP_DIST)


class Driver(object):
    def __init__(self, robo):
        self.__robo = robo
        self.__old_left, self.__old_right = 0, 0
        self.__left, self.__right = 0, 0

    def set(self, left, right):
        self.__left, self.__right = left, right

    def set_circular(self, radius, linear_speed, angular_speed):
        left, right = calculate(radius, linear_speed, angular_speed)
        self.__left, self.__right = left, right

    def change(self, left, right):
        self.__left += left
        self.__right += right

    def change_circular(self, radius, linear_speed, angular_speed):
        left, right = calculate(radius, linear_speed, angular_speed)
        self.__left += left
        self.__right += right

    def run(self):
        if abs(self.__old_left - self.__left) > 10 or abs(self.__old_right - self.__right) > 10:
            self.__old_left, self.__old_right = self.__left, self.__right

            self.__left = MAX_SPEED if self.__left > MAX_SPEED else -MAX_SPEED if self.__left < -MAX_SPEED else self.__left
            self.__right = MAX_SPEED if self.__right > MAX_SPEED else -MAX_SPEED if self.__right < -MAX_SPEED else self.__right

            self.__robo.send_motors_command(int(self.__left), int(self.__right), int(self.__left), int(self.__right))
        print 'drive: %d, %d' % (self.__left, self.__right)


class Controller(object):
    def __init__(self, eye, driver):
        self.__eye, self.__driver = eye, driver
        self.__left, self.__right = 0, 0

    def set(self, left, right):
        self.__left, self.__right = left, right

    def change(self, left, right):
        self.__left += left
        self.__right += right

    def run(self):
        left, right = self.__left, self.__right

        if left > 0 or right > 0:
            cur_angle = get_angle(left, right, 450)
            print 'cur angle: %d' % cur_angle

            scan = self.__eye.get()
            if scan is not None:
                scan = scan.get_points()
                min_distance = None

                for angle, distance in scan.items():
                    if distance > 30 and cur_angle - 30.0 < angle < cur_angle + 30.0:
                        if min_distance is None or distance < min_distance:
                            min_distance = distance

                if STOP_DIST < min_distance < LIMIT_DIST:
                    max_speed = get_max_speed(min_distance)
                    left = max_speed if left > max_speed else left
                    right = max_speed if right > max_speed else right

                elif min_distance <= STOP_DIST:
                    left, right = 0, 0

                print 'distance: %d' % min_distance
            else:
                print 'no scan!'

        self.__driver.set(left, right)


class Randomize(object):
    def __init__(self, driver, randomizing_width=20.0):
        self.__driver = driver
        self.__randomizing_width = randomizing_width

    def __randomize(self):
        return random.random() * self.__randomizing_width - self.__randomizing_width / 2.0

    def run(self):
        left, right = self.__randomize(), self.__randomize()
        self.__driver.change(left, right)
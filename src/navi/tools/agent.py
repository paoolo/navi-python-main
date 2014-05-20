import random

from navi.tools.logic import calculate


__author__ = 'paoolo'


class Eye(object):
    def __init__(self, laser):
        self.__laser, self.__scan = laser, None

    def get(self):
        return self.__scan

    def run(self):
        self.__scan = self.__laser.get_single_scan()


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
            self.__robo.send_motors_command(int(self.__left), int(self.__right), int(self.__left), int(self.__right))


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

        scan = self.__eye.get()
        # TODO(paoolo): use this scan to determine the path!
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
from tools.logic import calculate, check_trajectory

__author__ = 'paoolo'


class Eye(object):
    def __init__(self, laser):
        self.__laser, self.__scan = laser, None

    def get(self):
        return self.__scan

    def run(self):
        self.__scan = self.__laser.get_single_scan()


class Driver(object):
    def __init__(self, robo_front, robo_rear):
        self.__robo_front, self.__robo_rear = robo_front, robo_rear
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
            self.__robo_front.set_mixed_speed(int(self.__right), int(self.__left))
            self.__robo_rear.set_mixed_speed(int(self.__right), int(self.__left))


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
        if scan is not None:
            left, right = check_trajectory(scan, left, right)

        self.__driver.set(left, right)
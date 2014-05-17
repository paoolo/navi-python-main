# coding=utf-8
from random import random
import math
import threading
import time

__author__ = 'paoolo'

ALPHA = 0.2


def low_pass_filter_value(_new_value, _old_value=None, _alpha=ALPHA):
    """
    Low pass filter for one value.

    :param _new_value: number
    :param _old_value: number or None (default: None)
    :param _alpha: number or None (default: AlPHA)
    :return:
    """
    return _new_value if _old_value is None else _old_value + _alpha * (_new_value - _old_value)


def low_pass_filter_values(_new_value, _old_value=None, _alpha=ALPHA):
    """
    Low pass filter for tuple of values.

    :param _new_value: tuple of numbers
    :param _old_value: tuple of numbers or None (default: None)
    :param _alpha: number or None (default: ALPHA)
    :return:
    """
    _low_pass_lambda = lambda _val: low_pass_filter_value(_val[0], _val[1], _alpha)
    return _new_value if _old_value is None else tuple(map(_low_pass_lambda, zip(_new_value, _old_value)))


def _modify_values_randomly(_values):
    return tuple(map(lambda _val: _val + (random() - 0.5) * _val, _values))


def _generate_scan():
    _scan = Scan()
    _scan[-128] = int(random() * 50)
    for angle in range(-127, 128):
        value = random() * 100
        _scan[angle] = int(low_pass_filter_value(value, _scan[angle - 1], 0.185))
    return _scan


class Scan(dict):
    """
    Dictionary with override str(), repr() method.
    """

    def __init__(self, **kwargs):
        super(Scan, self).__init__(**kwargs)

    def __to_string(self):
        _out = ''
        for angle, distance in sorted(self.items()):
            _out += '% 4d=% 4d: %s\n' % (angle, distance, "*" * int(distance / 5))
        return _out

    def __str__(self):
        return self.__to_string()

    def __repr__(self):
        return self.__to_string()


class Point(object):
    """
    Tuple of position of the robot and orientation.
    """

    def __init__(self, x, y, fi):
        self.x, self.y, self.fi = x, y, fi


def get_point_for_scan(distance, angle):
    """
    For values (distance, angle) from scan compute relative coordinates of point.

    :param distance: number
    :param angle: number [rad]
    :return: tuple of two numbers (x, y)
    """
    return distance * math.sin(angle), distance * math.cos(angle)


def is_robot_on_goal(target_point, robot_point, epsilon=0.1):
    """
    Check if robot is on target.

    :param target_point: object of Point
    :param robot_point: object of Point
    :param epsilon: number
    :return: boolean if robot_point is on target_point
    """
    return math.pow(target_point.x - robot_point.x, 2) + math.pow(target_point.y - robot_point.y, 2) <= epsilon


def select_desired_steering_angle(gamma_ref, free_sectors):
    gamma_desired = None

    if gamma_ref in free_sectors:
        gamma_desired = gamma_ref
    else:
        # Identify gaps in the environment
        G_wide, G_medium, G_narrow = (), (), ()
        if G_wide:
            gamma_desired = min(G_wide)
        elif G_medium:
            gamma_desired = min(G_medium)
        elif G_narrow:
            gamma_desired = min(G_narrow)
        else:
            # Turn 180° around
            pass

    return gamma_desired


R = 1
r_large = 0.5  # [m]
d_safe2 = 1.2 * R
C_1 = 0.7
C_2 = 0.3


def configuration_space_algorithm():
    pass


def get_cost(gamma_ref, beta_j, c_1=C_1, c_2=C_2):
    return c_1 * (gamma_ref - beta_j) + c_2 * beta_j


def select_desired_turning_radius(L_min, gamma_desired, d_safe2, a, L_j=None, beta_j=None):
    L_j_m = math.sqrt((L_j * math.cos(beta_j + a)) ** 2 + (L_j * math.sin(beta_j)) ** 2)
    r_c = L_min / (2 * math.sin(gamma_desired))
    return (L_min - d_safe2, gamma_desired)


def turn_around_behavior():
    pass


class Robot():
    def __init__(self):
        self.left, self.right = 0, 0

    def set_velocity(self, left, right):
        """
        Set velocity.

        :param left: number
        :param right: number
        """
        self.left, self.right = right, left

    def get_velocity(self):
        return self.left, self.right

    def change_velocity(self, left, right):
        """
        Change velocity. Set difference.

        :param left: number
        :param right: number
        """
        self.left += left
        self.right += right

    def set_turn(self, velocity, turn):
        """
        Set turn with velocity and value turn in [-1..1].

        :param velocity: number positive
        :param turn: number in range [-1..1]
        """
        left = velocity if turn > 0 else 2 * velocity * turn + velocity
        right = velocity if turn < 0 else -2 * velocity * turn + velocity

        self.left, self.right = left, right

    def get_turn(self):
        if self.left > self.right:
            return self.left, (self.right - self.left) / (-2 * self.left)
        elif self.left < self.right:
            return self.right, (self.left - self.right) / (2 * self.right)
        else:
            # Value of self.left and self.right are the same.
            return self.left, 0

    def change_turn(self, velocity, turn):
        """
        Change turn with velocity and value turn in [-1..1]

        :param velocity: number positive
        :param turn: number around zero
        :return:
        """
        current_velocity, current_turn = self.get_turn()
        self.set_turn(current_velocity + velocity, current_turn + turn)


def where_i_can_drive(_scan):
    for angle, distance in sorted(_scan.items()):
        pass


old_values = None
values = (100, 100)

scan = _generate_scan()
print scan

for step in range(1, 100):
    values = low_pass_filter_values(values, old_values, ALPHA)
    old_values = values
    values = _modify_values_randomly(values)


def drive_to_point(x, y, _time=0.1):
    angle = math.atan(y / x)
    distance = math.sqrt(x ** 2 + y ** 2)
    radius = distance / (2 * math.cos(angle))
    street = 2 * radius * angle
    velocity = street / _time
    return angle, distance, radius, street, velocity


ROBO_WIDTH = 100.0


def get_drive_radius(left, right, robo_width=ROBO_WIDTH):
    left, right, robo_width = int(left), int(right), int(robo_width)

    if left == -right:
        return 0
    elif left == right:
        return None
    else:
        left, right, robo_width = float(left), float(right), float(robo_width)
        return robo_width * (right / (left - right) + 0.5)


def check_scan(_scan):
    for angle, distance in sorted(_scan.items()):
        pass


class State(object):
    robo_width = 100.0
    time_step = 0.2
    randomizing_width = 20.0
    targeting_width = 40.0

    def __init__(self):
        self.left, self.right = 0.0, 0.0
        self.x, self.y, self.angle = 0.0, 0.0, math.pi / 2
        self.target_x, self.target_y = 0.0, 0.0
        self.alive = True

        self.printing_thread = threading.Thread(target=self.printing)
        self.looking_thread = threading.Thread(target=self.looking)
        self.locating_thread = threading.Thread(target=self.locating)
        self.targeting_thread = threading.Thread(target=self.targeting)
        self.randomizing_thread = threading.Thread(target=self.randomizing)
        self.driving_thread = threading.Thread(target=self.driving)

        self.printing_thread.start()
        self.looking_thread.start()
        self.locating_thread.start()
        self.targeting_thread.start()
        self.randomizing_thread.start()
        self.driving_thread.start()

    def printing(self):
        while self.alive:
            print 'drive: % 4d, % 4d; target: % 4d, % 4d; location: % 4d, % 4d, % 4d' % (self.left, self.right,
                                                                                         self.target_x,
                                                                                         self.target_y,
                                                                                         self.x, self.y,
                                                                                         math.degrees(self.angle))
            time.sleep(State.time_step)

    def looking(self):
        while self.alive:
            time.sleep(State.time_step)

    def locating(self):
        while self.alive:
            left, right = self.left, self.right

            distance_traveled = State.time_step * (left + right) / 2.0
            radius = get_drive_radius(left, right, State.robo_width)

            if radius is None:
                # change in line
                self.x += distance_traveled * math.cos(self.angle)
                self.y += distance_traveled * math.sin(self.angle)

            elif radius is 0:
                # change angle only
                self.angle += distance_traveled / (2.0 * State.robo_width)

            else:
                # change on circle
                alpha = distance_traveled / radius
                self.angle += alpha
                self.x += radius * math.cos(alpha) * math.tan(alpha)
                self.y += radius * math.sin(alpha)

            if self.angle < -math.pi:
                self.angle += math.pi * 2.0
            elif self.angle > math.pi:
                self.angle -= math.pi * 2.0

            time.sleep(State.time_step)

    def targeting(self):
        randomize = lambda val: val + random() * State.targeting_width - State.targeting_width / 2.0

        while self.alive:
            self.target_x, self.target_y = map(randomize, (self.target_x, self.target_y))
            # wait until robo is on target
            time.sleep(State.time_step * 100)

    def randomizing(self):
        randomize = lambda val: val + random() * State.randomizing_width - State.randomizing_width / 2.0

        while self.alive:
            self.left, self.right = map(randomize, (self.left, self.right))
            time.sleep(State.time_step)

    def driving(self):
        while self.alive:
            # send value to robo
            time.sleep(State.time_step)

    def join(self):
        self.printing_thread.join()
        self.looking_thread.join()
        self.locating_thread.join()
        self.targeting_thread.join()
        self.randomizing_thread.join()
        self.driving_thread.join()


if __name__ == '__main__':
    state = State()
    state.join()
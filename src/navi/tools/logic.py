import math

from navi.tools import config

__author__ = 'paoolo'

SCANNER_DIST_OFFSET = float(config.SCANNER_DIST_OFFSET)
ANGLE_RANGE = float(config.ANGLE_RANGE)


def get_min_distance(scan, current_angle):
    scan = scan.get_points()
    min_distance = None
    min_distance_angle = None

    for angle, distance in scan.items():
        if distance > SCANNER_DIST_OFFSET \
            and current_angle - ANGLE_RANGE < angle < current_angle + ANGLE_RANGE:
            if min_distance is None or distance < min_distance:
                min_distance = distance
                min_distance_angle = angle

    return min_distance, min_distance_angle


HARD_LIMIT = float(config.HARD_LIMIT)
SOFT_LIMIT = float(config.SOFT_LIMIT)


def get_angle(left, right, robo_width):
    return math.degrees(math.atan((left - right) / float(robo_width)))

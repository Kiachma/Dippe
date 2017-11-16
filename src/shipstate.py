from __future__ import division
import position
import numpy as np
import math
import config
import copy


def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return (x, y)


def cart2pol(x, y):
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return (rho, phi)


class ShipState:
    def __init__(self, heading, position, speed, rate_of_turn):
        self.position = position
        self.speed = speed
        self.heading = heading
        self.rate_of_turn = rate_of_turn
        self.snapShot = None

    def update_position(self):
        prev = copy.deepcopy(self)
        prev.snapShot = None
        self.position = position.Position(self.position.get_x()
                                          + self.get_headingXY()[0] / ((config.playback['interval'] / 1000))
                                          * config.playback['rate'],
                                          self.position.get_y()
                                          + self.get_headingXY()[1] / ((config.playback['interval'] / 1000))
                                          * config.playback['rate'])
        self.snapShot = prev
        return self.position

    def standard_rate_turn(self, direction):
        correction = self.rate_of_turn * config.playback['interval'] / 1000 * config.playback[
            'rate']
        if direction == 'left':
            self.heading = self.heading - correction
            return -correction
        elif direction == 'right':
            self.heading = self.heading + correction
            return correction

    def slow_down(self):
        correction = - 1 * config.playback['interval'] / 1000 * config.playback[
            'rate']
        if self.speed + correction >= 0:

            self.speed = self.speed + correction

            return correction
        else:
            return 0

    def speed_up(self):
        correction = 1 * config.playback['interval'] / 1000 * config.playback[
            'rate']
        self.speed = self.speed + correction
        return correction

    def get_headingXY(self):
        # Remember to convert to radians!
        x, y = pol2cart(self.speed, math.radians(self.heading + 90))
        return [
            -x, y
        ]

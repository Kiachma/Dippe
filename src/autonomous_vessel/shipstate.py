from __future__ import division
from autonomous_vessel import position
import math
import config
import copy
import helpers


class ShipState:
    def __init__(self, heading, position_x, position_y, speed, max_speed, rate_of_turn):
        self.position = position.Position(position_x, position_y)
        self.speed = speed
        self.max_speed = max_speed
        self.heading = heading
        self.rate_of_turn = rate_of_turn

    def update_position(self):
        self.position.x = self.position.x + self.get_headingXY()[0] * config.playback['rate']
        self.position.y = self.position.y + self.get_headingXY()[1] * config.playback['rate']
        return self.position

    def standard_rate_turn(self, direction):
        correction = self.rate_of_turn * config.playback[
            'rate']
        if direction == 'left':
            self.heading = self.heading - correction
            return -correction
        elif direction == 'right':
            self.heading = self.heading + correction
            return correction

    def slow_down(self):
        correction = - 1 * config.playback[
            'rate']
        if self.speed + correction > 0:

            self.speed = self.speed + correction

            return correction
        else:
            return 0

    def speed_up(self):
        correction = 1 * config.playback[
            'rate']
        if correction + self.speed < self.max_speed:
            self.speed = self.speed + correction
            return correction
        else:
            self.speed = self.max_speed
            return self.max_speed - self.speed

    def get_headingXY(self):
        # Remember to convert to radians!
        x, y = helpers.pol2cart(self.speed * 1000 / 60 / 60, math.radians(self.heading + 90))
        return [
            -x, y
        ]

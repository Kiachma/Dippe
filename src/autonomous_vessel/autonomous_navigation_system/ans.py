import helpers
import math
from sortedcontainers import SortedDict
import config
import vesselService


class AutonomousNavigationSystem:
    def __init__(self, id, fis, ap):
        self.id = id
        self.heading_correction = 0
        self.speed_correction = 0
        self.fuzzy_inference_system = fis
        self.corrections = SortedDict()
        self.auto_pilot = ap
        self.min_col_time = math.inf
        self.prev_min_col_time = self.min_col_time

    def get_visible_vessels(self, shipstate):

        tmp = []
        for vessel in vesselService.vessels:
            if vessel.id != self.id:
                if helpers.distance(vessel.shipstate.position,
                                    shipstate.position) < config.visibility:
                    tmp.append(vessel)
        return tmp

    def next_position(self, shipstate):

        if self.auto_pilot:
            self.calculate_corrections(shipstate)
        return shipstate.update_position()

    def back_to_course(self, shipstate):
        if self.heading_correction != 0:
            if -shipstate.rate_of_turn >= self.heading_correction:
                self.heading_correction = self.heading_correction + shipstate.standard_rate_turn('right')

            elif self.heading_correction >= shipstate.rate_of_turn:
                self.heading_correction = self.heading_correction + shipstate.standard_rate_turn('left')
            elif self.heading_correction != 0:
                shipstate.heading = shipstate.heading + self.heading_correction
                self.heading_correction = 0

    def back_to_speed(self, shipstate):
        if self.speed_correction <= -1:
            self.speed_correction = self.speed_correction + shipstate.speed_up()
        elif self.speed_correction >= 1:
            self.speed_correction = self.speed_correction + shipstate.slow_down()

    def calculate_corrections(self, shipstate):
        self.corrections = SortedDict()
        self.prev_min_col_time = self.min_col_time
        self.min_col_time = math.inf
        for observed_vessel in self.get_visible_vessels(shipstate):
            main_observed, observed_main = helpers.cartesian_coords_to_relative(shipstate,
                                                                                observed_vessel.shipstate)

            vm = shipstate.speed
            vt = observed_vessel.shipstate.speed
            cm = math.radians(shipstate.heading)
            ct = math.radians(observed_vessel.shipstate.heading)

            vr = math.sqrt(pow(vm, 2) + pow(vt, 2) - 2 * vm * vt * math.cos(cm - ct))
            distance = helpers.distance(shipstate.position, observed_vessel.shipstate.position)
            time_until_collision = distance / vr
            if not self.min_col_time:
                self.min_col_time = time_until_collision
            else:
                self.min_col_time = min(self.min_col_time, time_until_collision)
            relative_course = observed_vessel.shipstate.heading - shipstate.heading
            if relative_course < 0:
                relative_course = 360 + relative_course
            if observed_vessel.shipstate.speed == 0:
                speed_ratio = 0
            elif shipstate.speed == 0:
                speed_ratio = 10
            else:
                speed_ratio = observed_vessel.shipstate.speed / shipstate.speed
            self.fuzzy_inference_system.input['bearing'] = main_observed
            self.fuzzy_inference_system.input['relative_course'] = relative_course
            self.fuzzy_inference_system.input['range'] = distance
            self.fuzzy_inference_system.input['speed_ratio'] = speed_ratio

            try:
                self.fuzzy_inference_system.compute()
                # self.fis.print_state()
                course_change = round(self.fuzzy_inference_system.output['course_change'])
                speed_change = round(self.fuzzy_inference_system.output['speed_change'])

                self.corrections[time_until_collision] = {'course_change': course_change,
                                                          "speed_change": speed_change,
                                                          "Target": observed_vessel.id}

            except ValueError as e:
                # pass
                # self.fis.print_state()
                print(e)
        if len(self.corrections) != 0:
            tot_weight = 0
            course_change = 0
            speed_change = 0
            for idx, correction in self.corrections.items():
                weight = 1 / idx
                tot_weight = tot_weight + weight
                course_change = correction['course_change'] * weight
                speed_change = correction['speed_change'] * weight
            course_change = course_change / tot_weight
            speed_change = speed_change / tot_weight
            print(self.id)
            print("Course change" + str(course_change))
            print("Speed change" + str(speed_change))
            if course_change >= shipstate.rate_of_turn:
                self.heading_correction = self.heading_correction + shipstate.standard_rate_turn('right')

            elif course_change <= -shipstate.rate_of_turn:
                self.heading_correction = self.heading_correction + shipstate.standard_rate_turn('left')
            elif course_change != 0:
                shipstate.heading = shipstate.heading + course_change
                self.heading_correction = self.heading_correction + course_change

            if speed_change > 1 * config.playback[
                'rate']:
                self.speed_correction = self.speed_correction + shipstate.speed_up()

            elif speed_change < -1 * config.playback[
                'rate']:
                self.speed_correction = self.speed_correction + shipstate.slow_down()
            elif speed_change != 0:
                shipstate.speed = shipstate.speed + speed_change
                self.speed_correction = self.speed_correction + speed_change

        else:
            if self.prev_min_col_time < self.min_col_time:
                self.back_to_course(shipstate)
                self.back_to_speed(shipstate)

            pass

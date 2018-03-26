import helpers
import math
from sortedcontainers import SortedDict
import config
import vesselService
import collections


class AutonomousNavigationSystem:
    def __init__(self, id, fis, ap):
        self.id = id
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
        diff = shipstate.target_heading - shipstate.heading
        heading_correction = (diff + 180) % 360 - 180
        if heading_correction < -shipstate.rate_of_turn:
            shipstate.standard_rate_turn('left')
        elif heading_correction > shipstate.rate_of_turn:
            shipstate.standard_rate_turn('right')
        elif heading_correction != 0:
            shipstate.heading = (shipstate.heading + heading_correction) % 360

        elif self.prev_min_col_time < self.min_col_time:
            diff = shipstate.orig_heading - shipstate.heading
            heading_correction = (diff + 180) % 360 - 180
            if heading_correction < 0:
                shipstate.target_heading = (shipstate.target_heading - shipstate.rate_of_turn / 2) % 360
            elif heading_correction > 0:
                shipstate.target_heading = (shipstate.target_heading + shipstate.rate_of_turn / 2) % 360

    def back_to_speed(self, shipstate):
        speed_correction = shipstate.target_speed - shipstate.speed
        if speed_correction <= -1:
            shipstate.slow_down()
        elif speed_correction >= 1:
            shipstate.speed_up()
        # elif self.prev_min_col_time < self.min_col_time:
        speed_correction = shipstate.orig_speed - shipstate.speed
        if speed_correction < 0:
            shipstate.target_speed = shipstate.target_speed - .5
        elif speed_correction > 0:
            shipstate.target_speed = shipstate.target_speed + .5

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
            time_until_collision = math.inf
            if vr != 0:
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
            self.fuzzy_inference_system.output = collections.OrderedDict()
            try:
                self.fuzzy_inference_system.compute()
                # self.fuzzy_inference_system.print_state()
            except ValueError as e:
                pass
                # print(e)
            if 'course_change' in self.fuzzy_inference_system.output or 'speed_change' in self.fuzzy_inference_system.output:
                self.corrections[time_until_collision] = {}
                self.corrections[time_until_collision]['target'] = observed_vessel.id
                if 'course_change' in self.fuzzy_inference_system.output:
                    course_change = round(self.fuzzy_inference_system.output['course_change'])
                    self.corrections[time_until_collision]['course_change'] = course_change
                if 'speed_change' in self.fuzzy_inference_system.output:
                    speed_change = round(self.fuzzy_inference_system.output['speed_change'])
                    self.corrections[time_until_collision]['speed_change'] = speed_change

        if len(self.corrections) != 0:
            course_tot_weight = 0
            speed_tot_weight = 0
            course_change = 0
            speed_change = 0
            for idx, correction in self.corrections.items():

                if 'course_change' in correction:
                    course_weight = 1 / idx
                    course_tot_weight = course_tot_weight + course_weight
                    course_change = course_change + correction['course_change'] * course_weight
                if 'speed_change' in correction:
                    speed_weight = 1 / idx
                    speed_tot_weight = speed_tot_weight + speed_weight
                    speed_change = speed_change + correction['speed_change'] * speed_weight
            if course_tot_weight != 0:
                course_change = course_change / course_tot_weight
                shipstate.target_heading = shipstate.heading + course_change
            if speed_tot_weight != 0:
                speed_change = speed_change / speed_tot_weight
                shipstate.target_speed = shipstate.speed + speed_change

            print(self.id)
            print("Course change" + str(course_change))
            print("Speed change" + str(speed_change))
            if course_change >= shipstate.rate_of_turn:
                shipstate.standard_rate_turn('right')

            elif course_change <= -shipstate.rate_of_turn:
                shipstate.standard_rate_turn('left')
            elif course_change != 0:
                if (shipstate.heading + course_change) % 360 >= 0:
                    shipstate.heading = (shipstate.heading + course_change) % 360
                else:
                    shipstate.heading = (shipstate.heading + 360 + course_change) % 360
            else:
                self.back_to_course(shipstate)
            if speed_change > 1 * config.playback[
                'rate']:
                shipstate.speed_up()

            elif speed_change < -1 * config.playback[
                'rate']:
                shipstate.slow_down()
            elif speed_change != 0:
                if shipstate.speed + speed_change >= 0:
                    shipstate.speed = shipstate.speed + speed_change
                else:
                    shipstate.speed = 0
            else:
                self.back_to_speed(shipstate)
        else:
            self.back_to_speed(shipstate)
            self.back_to_course(shipstate)

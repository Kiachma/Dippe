import collections
import json
import math

from sortedcontainers import SortedDict

import config
import helpers
import vesselService


class AutonomousNavigationSystem:
    def __init__(self, id, fis, ap):
        self.id = id
        self.fuzzy_inference_system = fis
        self.corrections = SortedDict()
        self.auto_pilot = ap
        self.min_col_time = math.inf
        self.prev_min_col_time = self.min_col_time
        self.prev_recc = dict()
        self.min_dist = dict(main=None, target=None, time=None, dist=9999)

    def get_visible_vessels(self, shipstate):

        tmp = []
        for vessel in vesselService.vessels:
            if vessel.id != self.id:
                if helpers.distance(vessel.shipstate.position,
                                    shipstate.position) < config.visibility:
                    tmp.append(vessel)
        return tmp

    def next_position(self, shipstate, i):

        if self.auto_pilot:
            self.calculate_corrections(shipstate, i)
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

        elif abs(self.prev_min_col_time) < abs(self.min_col_time) and not self.is_fis_corrections():
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
        if not self.is_fis_corrections():
            speed_correction = shipstate.orig_speed - shipstate.speed
            if speed_correction < 0:
                shipstate.target_speed = shipstate.target_speed - .5
            elif speed_correction > 0:
                shipstate.target_speed = shipstate.target_speed + .5

    def change(self, course, speed, target):

        if abs(speed) >= 1 or abs(course) >= 1:
            ret = True
        else:
            ret = False
        if target is None and ret:
            if 'TOT' in self.prev_recc and abs(self.prev_recc['TOT']['course'] - course) <= 1 and abs(
                    self.prev_recc['TOT']['speed'] - speed) <= 1:
                ret = False
            if 'TOT' in self.prev_recc:
                self.prev_recc['TOT']['course'] = course
                self.prev_recc['TOT']['speed'] = speed
            else:
                self.prev_recc['TOT'] = dict(course=course,
                                             speed=speed)
        elif ret:
            if target in self.prev_recc and abs(self.prev_recc[target]['course'] - course) <= 1 and abs(
                    self.prev_recc[target]['speed'] - speed) <= 1:
                ret = False
            if target in self.prev_recc:
                self.prev_recc[target]['course'] = course
                self.prev_recc[target]['speed'] = speed
            else:
                self.prev_recc[target] = dict(course=course,
                                              speed=speed)

        return ret

    def is_fis_corrections(self):
        return 'course_change' in self.fuzzy_inference_system.output or 'speed_change' in self.fuzzy_inference_system.output

    def calculate_corrections(self, shipstate, i):
        debug_strings = []
        self.corrections = SortedDict()
        self.prev_min_col_time = self.min_col_time
        self.min_col_time = math.inf
        course_change_proposed = False
        speed_change_proposed = False
        for observed_vessel in self.get_visible_vessels(shipstate):
            main_observed, observed_main = helpers.cartesian_coords_to_relative(shipstate,
                                                                                observed_vessel.shipstate)

            vm = shipstate.speed
            vt = observed_vessel.shipstate.speed
            cm = math.radians(shipstate.heading)
            ct = math.radians(observed_vessel.shipstate.heading)

            vr = -math.sqrt(pow(vm, 2) + pow(vt, 2) - 2 * vm * vt * math.cos(cm - ct))
            distance = helpers.distance(shipstate.position, observed_vessel.shipstate.position)
            if (distance < self.min_dist['dist']):
                self.min_dist['dist'] = distance
                self.min_dist['main'] = self.id
                self.min_dist['target'] = observed_vessel.id
                self.min_dist['time'] = i
            time_until_collision = math.inf
            course_diff = min((shipstate.heading - observed_vessel.shipstate.heading) % 360,
                              (observed_vessel.shipstate.heading - shipstate.heading) % 360)
            if 270 < main_observed <= 360 or 0 <= main_observed < 90:
                if course_diff < 90:
                    if vm > vt:
                        vr = -vr
                else:
                    vr = -vr

            elif 90 < main_observed < 270:
                if vm < vt and course_diff < 90:
                    vr = -vr
            else:
                if vm == 0 or vt == 0:
                    vr = -vr
            if vr != 0:
                time_until_collision = distance / abs(vr)
            else:
                time_until_collision = math.inf
            if not self.min_col_time:
                self.min_col_time = time_until_collision
            else:
                self.min_col_time = min(self.min_col_time, time_until_collision)
            if vr > 0:
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
                except ValueError as e:
                    pass
                    # print(e)
                if self.is_fis_corrections():
                    if self.change(
                            self.fuzzy_inference_system.output['course_change'],
                            self.fuzzy_inference_system.output['speed_change'],
                            observed_vessel.id):
                        self.corrections[time_until_collision] = {}
                        self.corrections[time_until_collision]['target'] = observed_vessel.id

                        if 'course_change' in self.fuzzy_inference_system.output:
                            course_change = self.fuzzy_inference_system.output['course_change']
                            self.corrections[time_until_collision]['course_change'] = course_change
                            course_change_proposed = True
                        if 'speed_change' in self.fuzzy_inference_system.output:
                            speed_change = self.fuzzy_inference_system.output['speed_change']
                            self.corrections[time_until_collision]['speed_change'] = speed_change
                            speed_change_proposed = True
                        if course_change_proposed or speed_change_proposed:
                            debug_strings.append("Target: " + str(observed_vessel.id))
                            debug_strings.append("Relative speed: " + str(vr))
                            debug_strings.append(self.fuzzy_inference_system.input.__repr__())
                            debug_strings.append(json.dumps(self.fuzzy_inference_system.output, indent=4))

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

        if course_change_proposed:
            course_change = course_change / course_tot_weight
            shipstate.target_heading = shipstate.heading + course_change
        if speed_change_proposed:
            speed_change = speed_change / speed_tot_weight
            shipstate.target_speed = shipstate.speed + speed_change
        course_change = round(course_change)
        speed_change = round(speed_change)
        if self.change(course_change, speed_change, None):
            print("i: " + str(i), file=open("Logs/" + config.name, "a"))
            print("Main: " + str(self.id), file=open("Logs/" + config.name, "a"))
            print("TOT:", file=open("Logs/" + config.name, "a"))
            print("Course change: " + str(course_change), file=open("Logs/" + config.name, "a"))
            print("Speed change: " + str(speed_change), file=open("Logs/" + config.name, "a"))
            for string__ in debug_strings:
                print(string__, file=open("Logs/" + config.name, "a"))
            print("__________________________________________________________________________________________________",
                  file=open("Logs/" + config.name, "a"))
        if course_change >= shipstate.rate_of_turn:
            shipstate.standard_rate_turn('right')

        elif course_change <= -shipstate.rate_of_turn:
            shipstate.standard_rate_turn('left')
        elif abs(course_change) >= 1:
            if (shipstate.heading + course_change) % 360 >= 0:
                shipstate.heading = (shipstate.heading + course_change) % 360
            else:
                shipstate.heading = (shipstate.heading + 360 + course_change) % 360
        elif not course_change_proposed:
            self.back_to_course(shipstate)
        if speed_change > 1 * config.playback[
            'rate']:
            shipstate.speed_up()

        elif speed_change < -1 * config.playback[
            'rate']:
            shipstate.slow_down()
        elif abs(speed_change) != 0:
            if shipstate.speed + speed_change >= 0:
                shipstate.speed = shipstate.speed + speed_change
            else:
                shipstate.speed = 0
        elif not speed_change_proposed:
            self.back_to_speed(shipstate)

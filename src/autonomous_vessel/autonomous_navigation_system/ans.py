from autonomous_vessel.autonomous_navigation_system import sa
from autonomous_vessel.autonomous_navigation_system import ca
import helpers
import math
from sortedcontainers import SortedDict
import config


class AutonomousNavigationSystem:
    def __init__(self, shipstate, id, fis, ap):
        self.id = id
        self.ca = ca.CollisionAvoidance()
        self.sa = sa.SituationalAwareness()
        self.shipstate = shipstate
        self.headingCorrection = 0
        self.speedCorrection = 0
        self.colission = False
        self.fis = fis
        self.corrections = SortedDict()
        self.i = 0
        self.ap = ap

    @property
    def next_position(self):

        if self.i == config.playback['rate'] and self.ap:
            self.calculate_corrections()
            self.i = 0
        self.i = self.i + 1
        return self.shipstate.update_position()

    def back_to_course(self):
        if self.headingCorrection != 0:
            if -self.shipstate.rate_of_turn <= self.headingCorrection < 0:
                self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('right')

            elif self.headingCorrection >= self.shipstate.rate_of_turn:
                self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('left')
            elif self.headingCorrection != 0:
                self.shipstate.heading = self.shipstate.heading + self.headingCorrection
                self.headingCorrection = 0

    def back_to_speed(self):
        if self.speedCorrection <= -1:
            self.speedCorrection = self.speedCorrection + self.shipstate.speed_up()
        elif self.speedCorrection >= 1:
            self.speedCorrection = self.speedCorrection + self.shipstate.slow_down()

    def calculate_corrections(self):
        self.corrections = SortedDict()
        for observed_vessel in self.sa.get_visible_vessels(self.shipstate):
            main_observed, observed_main = helpers.cartesian_coords_to_relative(self.shipstate,
                                                                                observed_vessel.ans.shipstate)

            vm = self.shipstate.speed
            vt = observed_vessel.ans.shipstate.speed
            cm = math.radians(self.shipstate.heading)
            ct = math.radians(observed_vessel.ans.shipstate.heading)
            vr = math.sqrt(pow(vm, 2) + pow(vt, 2) - 2 * vm * vt * math.cos(cm - ct))
            distance = helpers.distance(self.shipstate.position, observed_vessel.ans.shipstate.position)
            time_until_collision = distance / vr

            relative_course = observed_vessel.ans.shipstate.heading - self.shipstate.heading
            if relative_course < 0:
                relative_course = 360 + relative_course
            if observed_vessel.ans.shipstate.speed == 0:
                speed_ratio = 0
            elif self.shipstate.speed == 0:
                speed_ratio = 10
            else:
                speed_ratio = observed_vessel.ans.shipstate.speed / self.shipstate.speed
            self.fis.input['bearing'] = main_observed
            self.fis.input['relative_course'] = relative_course
            self.fis.input['range'] = distance
            self.fis.input['speed_ratio'] = speed_ratio

            try:
                self.fis.compute()
                course_change = round(self.fis.output['course_change'])
                speed_change = round(self.fis.output['speed_change'])

                # elif speed_change != 0 and self.shipstate.speed + self.fis.output[
                #     'speed_change'] >= 0:
                #     self.shipstate.speed = self.shipstate.speed + speed_change
                #     self.speedCorrection = self.speedCorrection + speed_change

                self.corrections[time_until_collision] = {'course_change': course_change,
                                                          "speed_change": speed_change,
                                                          "Target": observed_vessel.id}

            except ValueError:
                pass
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
            if course_change > self.shipstate.rate_of_turn:
                self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('right')

            elif course_change < -self.shipstate.rate_of_turn:
                self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('left')
            elif course_change != 0:
                self.shipstate.heading = self.shipstate.heading + course_change
                self.headingCorrection = self.headingCorrection + course_change

            if speed_change > 1:
                self.speedCorrection = self.speedCorrection + self.shipstate.speed_up()

            elif speed_change < -1:
                self.speedCorrection = self.speedCorrection + self.shipstate.slow_down()
        else:
            self.back_to_course()
            self.back_to_speed()
            # elif self.speedCorrection != 0 and self.shipstate.speed + speed_change >= 0:
            #     self.shipstate.speed = self.shipstate.speed + self.speedCorrection
            #     self.speedCorrection = 0

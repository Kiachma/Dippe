import ca
import sa

import helpers
import math


class AutonomousNavigationSystem:
    def __init__(self, shipstate, id, fis):
        self.id = id
        self.ca = ca.CollisionAvoidance()
        self.sa = sa.SituationalAwareness()
        self.shipstate = shipstate
        self.headingCorrection = 0
        self.speedCorrection = 0
        self.colission = False
        self.fis = fis

    def next_position(self):
        # self.colission = False
        # self.ca.reset_risks()
        # for observed_vessel in self.sa.get_visible_vessels(self.shipstate):
        #     self.ca.crossing(observed_vessel.autonomous_navigation_system.shipstate, self.shipstate)
        #     self.ca.head_on(observed_vessel.autonomous_navigation_system.shipstate, self.shipstate)
        #     self.ca.overtaking(observed_vessel.autonomous_navigation_system.shipstate, self.shipstate)
        #
        # if self.ca.risks['head_on'] or self.ca.risks['crossing'] or self.ca.risks['overtaking']:
        #     self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('right')
        #     if not self.ca.risks['overtaking']:
        #         self.speedCorrection = self.speedCorrection + self.shipstate.slow_down()
        #     self.colission = True
        # elif self.headingCorrection != 0 or self.speedCorrection != 0:
        #     if self.headingCorrection < 0:
        #         self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('right')
        #     if self.headingCorrection > 0:
        #         self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('left')
        #
        #     if self.speedCorrection < 0:
        #         self.speedCorrection = self.speedCorrection + self.shipstate.speed_up()
        #     if self.speedCorrection > 0:
        #         self.speedCorrection = self.speedCorrection + self.shipstate.slow_down()
        #
        # return self.shipstate.update_position()
        for observed_vessel in self.sa.get_visible_vessels(self.shipstate):
            main_observed, observed_main = helpers.cartesian_coords_to_relative(self.shipstate,
                                                                                observed_vessel.ans.shipstate)

            # vm = self.shipstate.speed
            # vt = observed_vessel.ans.shipstate.speed
            cm = math.radians(self.shipstate.heading)
            ct = math.radians(observed_vessel.ans.shipstate.heading)
            # vr = math.sqrt(pow(vm, 2) + pow(vt, 2) - 2 * vm * vt * math.cos(cm - ct))
            # relative_course = math.degrees(ct - math.acos((pow(vr, 2) + pow(vt, 2) - pow(vm, 2)) / (2 * vr * vt)))
            relative_course = observed_vessel.ans.shipstate.heading - self.shipstate.heading
            if relative_course < 0:
                relative_course = 360 + relative_course
            self.fis.input['bearing'] = main_observed
            self.fis.input['relative_course'] = relative_course
            self.fis.input['range'] = helpers.distance(self.shipstate.position, observed_vessel.ans.shipstate.position)
            self.fis.input['speed_ratio'] = observed_vessel.ans.shipstate.speed / self.shipstate.speed
            try:
                self.fis.compute()
                print self.fis.output['course_change']
                print self.fis.output['speed_change']
                if self.fis.output['course_change'] > self.shipstate.rate_of_turn:
                    self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('right')

                elif self.fis.output['course_change'] < -self.shipstate.rate_of_turn:
                    self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('left')
                elif self.fis.output['course_change'] != 0:
                    self.shipstate.heading = self.shipstate.heading + self.fis.output['course_change']
                    self.headingCorrection = self.headingCorrection + self.fis.output['course_change']

                if self.fis.output['speed_change'] > 1:
                    self.speedCorrection = self.speedCorrection + self.shipstate.speed_up()

                elif self.fis.output['speed_change'] < -1:
                    self.speedCorrection = self.speedCorrection + self.shipstate.slow_down()
                elif self.fis.output['speed_change'] != 0:
                    self.shipstate.speed = self.shipstate.speed + self.fis.output['speed_change']
                    self.speedCorrection = self.speedCorrection + self.fis.output['speed_change']



            except ValueError:
                if self.headingCorrection != 0 or self.speedCorrection != 0:
                    if -self.shipstate.rate_of_turn <= self.headingCorrection < 0:
                        self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('right')

                    elif 0 < self.headingCorrection >= self.shipstate.rate_of_turn:
                        self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('left')
                    elif self.headingCorrection != 0:
                        self.shipstate.heading = self.shipstate.heading + self.headingCorrection
                        self.headingCorrection = 0

                    if 0 < self.speedCorrection <= 1:
                        self.speedCorrection = self.speedCorrection + self.shipstate.speed_up()
                    if -1 <= self.speedCorrection < 0:
                        self.speedCorrection = self.speedCorrection + self.shipstate.slow_down()

                    elif self.speedCorrection != 0:
                        self.shipstate.speed = self.shipstate.speed + self.speedCorrection
                        self.speedCorrection = 0
        return self.shipstate.update_position()

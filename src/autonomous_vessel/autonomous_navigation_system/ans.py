from autonomous_vessel.autonomous_navigation_system import sa
from autonomous_vessel.autonomous_navigation_system import ca
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

    @property
    def next_position(self):
        for observed_vessel in self.sa.get_visible_vessels(self.shipstate):
            main_observed, observed_main = helpers.cartesian_coords_to_relative(self.shipstate,
                                                                                observed_vessel.ans.shipstate)

            relative_course = observed_vessel.ans.shipstate.heading - self.shipstate.heading
            if relative_course < 0:
                relative_course = 360 + relative_course
            if observed_vessel.ans.shipstate.speed == 0:
                speed_ratio = 0
            elif self.shipstate.speed == 0:
                speed_ratio = 10
            else:
                speed_ratio = observed_vessel.ans.shipstate.speed / self.shipstate.speed
            range = helpers.distance(self.shipstate.position, observed_vessel.ans.shipstate.position)
            print("----------------------------------")
            print(str(self.id))
            print("heading: " + str(self.shipstate.heading))
            print("speed: " + str(self.shipstate.speed))
            print("bearing: " + str(main_observed))
            print("relative_course: " + str(relative_course))
            print("range: " + str(range))
            print("ratio: " + str(speed_ratio))
            self.fis.input['bearing'] = main_observed
            self.fis.input['relative_course'] = relative_course
            self.fis.input['range'] = range
            self.fis.input['speed_ratio'] = speed_ratio

            course_change = 0
            speed_change = 0
            try:
                self.fis.compute()
                course_change = round(self.fis.output['course_change'])
                speed_change = round(self.fis.output['speed_change'])

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
                # elif speed_change != 0 and self.shipstate.speed + self.fis.output[
                #     'speed_change'] >= 0:
                #     self.shipstate.speed = self.shipstate.speed + speed_change
                #     self.speedCorrection = self.speedCorrection + speed_change



            except ValueError:
                pass
            if course_change == 0:
                if self.headingCorrection != 0:
                    if -self.shipstate.rate_of_turn <= self.headingCorrection < 0:
                        self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('right')

                    elif self.headingCorrection >= self.shipstate.rate_of_turn:
                        self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('left')
                    elif self.headingCorrection != 0:
                        self.shipstate.heading = self.shipstate.heading + self.headingCorrection
                        self.headingCorrection = 0
            if speed_change == 0:
                if self.speedCorrection <= -1:
                    self.speedCorrection = self.speedCorrection + self.shipstate.speed_up()
                elif self.speedCorrection >= 1:
                    self.speedCorrection = self.speedCorrection + self.shipstate.slow_down()

                    # elif self.speedCorrection != 0 and self.shipstate.speed + speed_change >= 0:
                    #     self.shipstate.speed = self.shipstate.speed + self.speedCorrection
                    #     self.speedCorrection = 0
        return self.shipstate.update_position()

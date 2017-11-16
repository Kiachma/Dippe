import ca
import sa
import config
import math
import copy


class AutonomousNavigationSystem:
    def __init__(self, shipstate, id):
        self.id = id
        self.ca = ca.CollisionAvoidance()
        self.sa = sa.SituationalAwareness()
        self.shipstate = shipstate
        self.headingCorrection = 0
        self.speedCorrection = 0
        self.colission = False

    def next_position(self):
        self.colission = False
        self.ca.reset_risks()
        for observed_vessel in self.sa.get_visible_vessels(self.shipstate):
            self.ca.crossing(observed_vessel.ans.shipstate, self.shipstate)
            self.ca.head_on(observed_vessel.ans.shipstate, self.shipstate)
            self.ca.overtaking(observed_vessel.ans.shipstate, self.shipstate)

        if self.ca.risks['head_on'] or self.ca.risks['crossing'] or self.ca.risks['overtaking']:
            self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('right')
            if not self.ca.risks['overtaking']:
                self.speedCorrection = self.speedCorrection + self.shipstate.slow_down()
            self.colission = True
        elif self.headingCorrection != 0 or self.speedCorrection != 0:
            if self.headingCorrection < 0:
                self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('right')
            if self.headingCorrection > 0:
                self.headingCorrection = self.headingCorrection + self.shipstate.standard_rate_turn('left')

            if self.speedCorrection < 0:
                self.speedCorrection = self.speedCorrection + self.shipstate.speed_up()
            if self.speedCorrection > 0:
                self.speedCorrection = self.speedCorrection + self.shipstate.slow_down()

        return self.shipstate.update_position()

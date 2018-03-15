from autonomous_vessel.autonomous_navigation_system import ans
from autonomous_vessel import shipstate
import math


class Vessel:
    def __init__(self, id, heading, position_x, position_y,
                 speed, max_speed, rate_of_turn, fis, ap):
        self.id = id
        self.shipstate = shipstate.ShipState(heading, position_x, position_y,
                                             speed, max_speed, rate_of_turn)

        self.ans = ans.AutonomousNavigationSystem(self.id, fis, ap)

    def next_position(self):
        return self.ans.next_position(self.shipstate)

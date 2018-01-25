from autonomous_vessel.autonomous_navigation_system import ans
import math


class Vessel:
    def __init__(self, id, shipState, fis, ap):
        self.id = id
        self.ans = ans.AutonomousNavigationSystem(shipState, self.id, fis, ap)
        self.artists = dict()


class KnownVessel(Vessel):
    def __init__(self, id, shipState):
        Vessel.__init__(self, id, shipState, False, False)
        self.sector_to = None
        self.sector_from = None

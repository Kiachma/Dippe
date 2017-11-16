import ans
import math


class Vessel:
    def __init__(self, id, shipState):
        self.id = id
        self.ans = ans.AutonomousNavigationSystem(shipState, self.id)
        self.artists = dict()


class KnownVessel(Vessel):
    def __init__(self, id, shipState):
        Vessel.__init__(self, id, shipState)
        self.sector_to = None
        self.sector_from = None

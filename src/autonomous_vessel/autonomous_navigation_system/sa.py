import config
import helpers


class SituationalAwareness:
    def __init__(self):
        self.knownVessels = dict()
        self.sectors = [{} for _ in range(16)]

    def get_visible_vessels(self, shipstate):

        tmp = []
        for id, vessel in self.knownVessels.items():
            if helpers.distance(vessel.ans.shipstate.position,
                                shipstate.position) < config.visibility:
                tmp.append(vessel)
        return tmp

    def get_known_vessels(self, shipstate):
        return self.knownVessels

    def add_observed_vessel(self, vessel):
        self.knownVessels[vessel.id] = vessel

    def populate_sectors(self, opras):
        self.sectors = [{} for _ in range(16)]
        for relation in opras:
            other_vessel = self.knownVessels[relation['to']]
            other_vessel.sector_to = relation['OPRA1']
            other_vessel.sector_from = relation['OPRA2']
            self.sectors[relation['OPRA1']][relation['to']] = other_vessel

import config
import helpers
import math


def is_head_on(bearing):
    right = 0 <= bearing <= config.sectors['headOn'][1]
    left = config.sectors['headOn'][0] <= bearing <= 360
    return left or right


def is_crossing_give_way(bearing):
    return config.sectors['crossing_give_way'][0] <= bearing <= config.sectors['crossing_give_way'][1]


def is_crossing_stand_on(bearing):
    return config.sectors['crossing_stand_on'][0] <= bearing <= config.sectors['crossing_stand_on'][1]


def is_overtaking_give_way(bearing):
    left = config.sectors['over_take_give_way'][0] <= bearing <= 360
    right = 0 <= bearing <= config.sectors['over_take_give_way'][1]
    return left or right


def is_overtaking_stand_on(bearing):
    return config.sectors['over_take_stand_on'][0] <= bearing <= config.sectors['over_take_stand_on'][1]


class CollisionAvoidance:
    def __init__(self):
        self.risks = {
            'head_on': [],
            'crossing': [],
            'overtaking': [],
        }

    def reset_risks(self):
        self.risks['head_on'] = []
        self.risks['crossing'] = []
        self.risks['overtaking'] = []

    def head_on(self, observed_vessel, shipstate):

        main_observed, observed_main = helpers.cartesian_coords_to_relative(shipstate, observed_vessel)
        if is_head_on(main_observed) and (
                    is_head_on(observed_main) or observed_vessel.speed == 0) and self.relative_bearing_same(
            observed_vessel, shipstate):
            observed_vessel.bearing = main_observed
            self.risks['head_on'].append(observed_vessel)
            return True

        return False

    def crossing(self, observed_vessel, shipstate):
        main_observed, observed_main = helpers.cartesian_coords_to_relative(shipstate, observed_vessel)

        if is_crossing_give_way(main_observed) and is_crossing_stand_on(observed_main) and self.relative_bearing_same(
                observed_vessel, shipstate):
            self.risks['crossing'].append(observed_vessel)
            return True
        return False

    def overtaking(self, observed_vessel, shipstate):
        main_observed, observed_main = helpers.cartesian_coords_to_relative(shipstate, observed_vessel)

        if observed_vessel.snapShot is not None and shipstate.snapShot is not None:
            old_distance = helpers.distance(observed_vessel.snapShot.position,
                                            shipstate.snapShot.position)
            new_distance = helpers.distance(observed_vessel.position, shipstate.position)
            if is_overtaking_give_way(main_observed) and is_overtaking_stand_on(
                    observed_main) and old_distance > new_distance and self.relative_bearing_same(
                observed_vessel, shipstate):
                self.risks['overtaking'].append(observed_vessel)
                return True

        return False

    def relative_bearing_same(self, shipstateA, shipstateB):
        if shipstateA.snapShot is None or shipstateB.snapShot is None:
            return False
        current = helpers.calculate_initial_compass_bearing((shipstateA.position.x, shipstateA.position.y),
                                                            (shipstateB.position.x, shipstateB.position.y))
        prev = helpers.calculate_initial_compass_bearing(
            (shipstateA.snapShot.position.x, shipstateA.snapShot.position.y),
            (shipstateB.snapShot.position.x, shipstateB.snapShot.position.y))

        current = helpers.compass_to_relative(current, shipstateA.heading)
        prev = helpers.compass_to_relative(prev, shipstateA.heading)
        distance = helpers.distance(shipstateA.snapShot.position, shipstateB.snapShot.position)

        return abs(prev - current) < 10

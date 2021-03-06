import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

import config


def generate_trapetzoid(start, end, buffer):
    return [(start - buffer / 2) if start - buffer > 0 else 0,
            start + buffer / 2 if start > 0 else 0,
            end - buffer / 2 if end < 360 else 360,
            (end + buffer / 2) if end + buffer < 360 else 360]
    pass


def init_fuzzy():
    # Generate universe variables

    bear = ctrl.Antecedent(np.arange(0, 360, 1), 'bearing')
    range = ctrl.Antecedent(np.arange(0, config.radius['ra'] / 1000+10, 0.1 / config.scale), 'range')
    rel_course = ctrl.Antecedent(np.arange(0, 360, 1), 'relative_course')
    speed_ratio = ctrl.Antecedent(np.arange(0, 10, 0.1), 'speed_ratio')
    course_change = ctrl.Consequent(np.arange(-40, 40, 1), 'course_change')
    speed_change = ctrl.Consequent(np.arange(-10, 10, 1), 'speed_change')

    #
    # Generate fuzzy membership functions

    bear['1'] = fuzz.trapmf(bear.universe, generate_trapetzoid(0, 5, 5))
    bear['2'] = fuzz.trapmf(bear.universe, generate_trapetzoid(5, 85, 5))
    bear['3'] = fuzz.trapmf(bear.universe, generate_trapetzoid(85, 95, 5))
    bear['4'] = fuzz.trapmf(bear.universe, generate_trapetzoid(95, 175, 5))
    bear['5'] = fuzz.trapmf(bear.universe, generate_trapetzoid(175, 185, 5))
    bear['6'] = fuzz.trapmf(bear.universe, generate_trapetzoid(185, 211, 5))
    bear['7'] = fuzz.trapmf(bear.universe, generate_trapetzoid(211, 265, 5))
    bear['8'] = fuzz.trapmf(bear.universe, generate_trapetzoid(265, 275, 5))
    bear['9'] = fuzz.trapmf(bear.universe, generate_trapetzoid(275, 329, 5))
    bear['10'] = fuzz.trapmf(bear.universe, generate_trapetzoid(329, 355, 5))
    bear['1b'] = fuzz.trapmf(bear.universe, generate_trapetzoid(355, 360, 5))

    range['rvd'] = fuzz.trapmf(range.universe, [0,
                                                0,
                                                config.radius['rvd'] / 1000 - 0.3 / config.scale,
                                                config.radius['rvd'] / 1000 + 0.3 / config.scale
                                                ])
    range['rb'] = fuzz.trapmf(range.universe, [config.radius['rvd'] / 1000 - 0.3 / config.scale,
                                               config.radius['rvd'] / 1000 + 0.3 / config.scale,
                                               config.radius['rb'] / 1000 - 0.3 / config.scale,
                                               config.radius['rb'] / 1000 + 0.3 / config.scale
                                               ])
    range['ra'] = fuzz.trapmf(range.universe, [config.radius['rb'] / 1000 - 0.3 / config.scale,
                                               config.radius['rb'] / 1000 + 0.3 / config.scale,
                                               config.radius['ra'] / 1000,
                                               config.radius['ra'] / 1000+10
                                               ])

    rel_course['a'] = fuzz.trapmf(rel_course.universe, generate_trapetzoid(0, 22.5, 5))
    rel_course['b'] = fuzz.trapmf(rel_course.universe, generate_trapetzoid(22.5, 67.5, 5))
    rel_course['c'] = fuzz.trapmf(rel_course.universe, generate_trapetzoid(67.5, 112.5, 5))
    rel_course['d'] = fuzz.trapmf(rel_course.universe, generate_trapetzoid(112.5, 157.5, 5))
    rel_course['e'] = fuzz.trapmf(rel_course.universe, generate_trapetzoid(157.5, 202.5, 5))
    rel_course['f'] = fuzz.trapmf(rel_course.universe, generate_trapetzoid(202.5, 247.5, 5))
    rel_course['g'] = fuzz.trapmf(rel_course.universe, generate_trapetzoid(247.5, 292.5, 5))
    rel_course['h'] = fuzz.trapmf(rel_course.universe, generate_trapetzoid(292.5, 337.5, 5))
    rel_course['ab'] = fuzz.trapmf(rel_course.universe, generate_trapetzoid(337.5, 360, 5))

    speed_ratio['1'] = fuzz.trapmf(speed_ratio.universe, [0,
                                                          0,
                                                          0.8 - .05,
                                                          0.8 + .05
                                                          ])
    speed_ratio['2'] = fuzz.trapmf(speed_ratio.universe, [0.8 - .05,
                                                          0.8 - .05,
                                                          1.2 - .05,
                                                          1.2 + .05
                                                          ])
    speed_ratio['3'] = fuzz.trapmf(speed_ratio.universe, [1.2 - .05,
                                                          1.2 - .05,
                                                          10,
                                                          10
                                                          ])

    course_change['port'] = fuzz.trapmf(course_change.universe, [-40,
                                                                 -40,
                                                                 -10 - 5,
                                                                 -10 + 5
                                                                 ])
    course_change['keep'] = fuzz.trapmf(course_change.universe, [-10 - 5,
                                                                 -10 + 5,
                                                                 10 - 5,
                                                                 10 + 5
                                                                 ])
    course_change['starboard'] = fuzz.trapmf(course_change.universe, [10 - 5,
                                                                      10 + 5,
                                                                      40,
                                                                      40
                                                                      ])

    speed_change['decrease'] = fuzz.trapmf(speed_change.universe, [-10,
                                                                   -10,
                                                                   -2 - 1,
                                                                   -2 + 1
                                                                   ])
    speed_change['keep'] = fuzz.trapmf(speed_change.universe, [-2 - 1,
                                                               -2 + 1,
                                                               2 - 1,
                                                               2 + 1
                                                               ])
    speed_change['increase'] = fuzz.trapmf(speed_change.universe, [2 - 1,
                                                                   2 + 1,
                                                                   10,
                                                                   10
                                                                   ])
    bear.view()
    rel_course.view()
    range.view()
    speed_ratio.view()
    course_change.view()
    speed_change.view()
    rules = []

    # bear.view()
    # rel_course.view()
    # range.view()
    # speed_ratio.view()
    # course_change.view()
    # speed_change.view()
    def add_rule(bearings, course, speed, include_rvd, course_chg, speed_chg):
        consequents = []
        if course_chg and speed_chg:
            consequents = (course_change[course_chg], speed_change[speed_chg])
        elif speed_chg:
            consequents = ( course_change['keep'],speed_change[speed_chg])
        elif course_chg:
            consequents = (course_change[course_chg],speed_change['keep'])
        else:
            consequents = (course_change['keep'], speed_change['keep'])

        if include_rvd:
            rules.append(ctrl.Rule(
                bear[bearings] &
                rel_course[course] &
                speed_ratio[str(speed)] &
                (range['rvd'] | range['rb']),
                consequents)
            )
        else:
            rules.append(ctrl.Rule(
                bear[bearings] &
                rel_course[course] &
                speed_ratio[str(speed)] &
                (range['ra'] | range['rb'] | range['rvd']),
                consequents)
            )

    # add_rule(bearing, rel_course, speed_ratio, include_rvd, course_change, speed_change)
    add_rule('1', 'd', 1, True, False, False)
    add_rule('1b', 'd', 1, True, False, False)
    add_rule('1', 'd', 1, False, False, False)
    add_rule('1b', 'd', 1, False, False, False)

    add_rule('1', 'd', 2, True, False, False)
    add_rule('1b', 'd', 2, True, False, False)
    add_rule('1', 'd', 2, False, False, False)
    add_rule('1b', 'd', 2, False, False, False)

    add_rule('1', 'd', 3, True, False, False)
    add_rule('1b', 'd', 3, True, False, False)
    add_rule('1', 'd', 3, False, False, False)
    add_rule('1b', 'd', 3, False, False, False)

    add_rule('1', 'e', 1, True, 'starboard', False)
    add_rule('1b', 'e', 1, True, 'starboard', False)
    add_rule('1', 'e', 1, False, 'starboard', False)
    add_rule('1b', 'e', 1, False, 'starboard', False)

    add_rule('1', 'e', 2, True, 'starboard', False)
    add_rule('1b', 'e', 2, True, 'starboard', False)
    add_rule('1', 'e', 2, False, 'starboard', False)
    add_rule('1b', 'e', 2, False, 'starboard', False)

    add_rule('1', 'e', 3, True, 'starboard', False)
    add_rule('1b', 'e', 3, True, 'starboard', False)
    add_rule('1', 'e', 3, False, 'starboard', False)
    add_rule('1b', 'e', 3, False, 'starboard', False)

    add_rule('1', 'f', 1, True, False, False)
    add_rule('1b', 'f', 1, True, False, False)
    add_rule('1', 'f', 1, False, False, False)
    add_rule('1b', 'f', 1, False, False, False)

    add_rule('1', 'f', 2, True, False, False)
    add_rule('1b', 'f', 2, True, False, False)
    add_rule('1', 'f', 2, False, False, False)
    add_rule('1b', 'f', 2, False, False, False)

    add_rule('1', 'f', 3, True, False, False)
    add_rule('1b', 'f', 3, True, False, False)
    add_rule('1', 'f', 3, False, False, False)
    add_rule('1b', 'f', 3, False, False, False)

    add_rule('2', 'e', 1, True, False, False)
    add_rule('2', 'e', 2, True, False, 'increase')
    add_rule('2', 'e', 3, True, False, 'increase')
    add_rule('2', 'e', 1, False, False, False)
    add_rule('2', 'e', 2, False, False, 'increase')
    add_rule('2', 'e', 3, False, False, 'increase')

    add_rule('2', 'f', 1, True, False, False)
    add_rule('2', 'f', 2, True, 'starboard', 'decrease')
    add_rule('2', 'f', 3, True, 'starboard', 'decrease')
    add_rule('2', 'f', 1, False, False, False)
    add_rule('2', 'f', 2, False, 'starboard', 'decrease')
    add_rule('2', 'f', 3, False, 'starboard', 'decrease')

    add_rule('2', 'g', 1, True, False, False)
    add_rule('2', 'g', 2, True, 'starboard', False)
    add_rule('2', 'g', 3, True, 'starboard', False)
    add_rule('2', 'g', 1, False, False, False)
    add_rule('2', 'g', 2, False, 'starboard', False)
    add_rule('2', 'g', 3, False, 'starboard', False)

    add_rule('3', 'f', 1, True, False, False)
    add_rule('3', 'f', 2, True, False, 'increase')
    add_rule('3', 'f', 3, True, False, 'increase')
    add_rule('3', 'f', 1, False, False, False)
    add_rule('3', 'f', 2, False, False, 'increase')
    add_rule('3', 'f', 3, False, False, 'increase')

    add_rule('3', 'g', 1, True, False, False)
    add_rule('3', 'g', 2, True, False, 'decrease')
    add_rule('3', 'g', 3, True, False, 'decrease')
    add_rule('3', 'g', 1, False, False, False)
    add_rule('3', 'g', 2, False, False, 'decrease')
    add_rule('3', 'g', 3, False, False, 'decrease')

    add_rule('3', 'h', 1, True, False, False)
    add_rule('3', 'h', 2, True, False, 'decrease')
    add_rule('3', 'h', 3, True, False, 'decrease')
    add_rule('3', 'h', 1, False, False, False)
    add_rule('3', 'h', 2, False, False, 'decrease')
    add_rule('3', 'h', 3, False, False, 'decrease')

    add_rule('4', 'g', 1, True, False, False)
    add_rule('4', 'g', 2, True, False, 'increase')
    add_rule('4', 'g', 3, True, False, 'increase')
    add_rule('4', 'g', 1, False, False, False)
    add_rule('4', 'g', 2, False, False, 'increase')
    add_rule('4', 'g', 3, False, False, 'increase')

    add_rule('4', 'h', 1, True, False, False)
    add_rule('4', 'h', 2, True, 'port', 'decrease')
    add_rule('4', 'h', 3, True, 'port', 'decrease')
    add_rule('4', 'h', 1, False, False, False)
    add_rule('4', 'h', 2, False, False, False)
    add_rule('4', 'h', 3, False, False, False)

    add_rule('4', 'a', 1, True, False, False)
    add_rule('4', 'a', 2, True, 'port', 'decrease')
    add_rule('4', 'a', 3, True, 'port', 'decrease')
    add_rule('4', 'a', 1, False, False, False)
    add_rule('4', 'a', 2, False, False, False)
    add_rule('4', 'a', 3, False, False, False)
    add_rule('4', 'ab', 1, True, False, False)
    add_rule('4', 'ab', 2, True, 'port', 'decrease')
    add_rule('4', 'ab', 3, True, 'port', 'decrease')
    add_rule('4', 'ab', 1, False, False, False)
    add_rule('4', 'ab', 2, False, False, False)
    add_rule('4', 'ab', 3, False, False, False)

    add_rule('5', 'h', 1, True, False, False)
    add_rule('5', 'h', 2, True, False, False)
    add_rule('5', 'h', 3, True, False, False)
    add_rule('5', 'h', 1, False, False, False)
    add_rule('5', 'h', 2, False, False, False)
    add_rule('5', 'h', 3, False, False, False)

    add_rule('5', 'a', 1, True, 'port', False)
    add_rule('5', 'a', 2, True, 'port', False)
    add_rule('5', 'a', 3, True, 'port', False)
    add_rule('5', 'a', 1, False, False, False)
    add_rule('5', 'a', 2, False, False, False)
    add_rule('5', 'a', 3, False, False, False)

    add_rule('5', 'b', 1, True, False, False)
    add_rule('5', 'b', 2, True, False, False)
    add_rule('5', 'b', 3, True, False, False)
    add_rule('5', 'b', 1, False, False, False)
    add_rule('5', 'b', 2, False, False, False)
    add_rule('5', 'b', 3, False, False, False)

    add_rule('6', 'a', 1, True, False, False)
    add_rule('6', 'a', 2, True, False, 'decrease')
    add_rule('6', 'a', 3, True, False, 'decrease')
    add_rule('6', 'a', 1, False, False, False)
    add_rule('6', 'a', 2, False, False, False)
    add_rule('6', 'a', 3, False, False, False)
    add_rule('6', 'ab', 1, True, False, False)
    add_rule('6', 'ab', 2, True, False, 'decrease')
    add_rule('6', 'ab', 3, True, False, 'decrease')
    add_rule('6', 'ab', 1, False, False, False)
    add_rule('6', 'ab', 2, False, False, False)
    add_rule('6', 'ab', 3, False, False, False)

    add_rule('6', 'b', 1, True, False, False)
    add_rule('6', 'b', 2, True, False, 'decrease')
    add_rule('6', 'b', 3, True, False, 'decrease')
    add_rule('6', 'b', 1, False, False, False)
    add_rule('6', 'b', 2, False, False, False)
    add_rule('6', 'b', 3, False, False, False)

    add_rule('6', 'c', 1, True, False, False)
    add_rule('6', 'c', 2, True, False, 'increase')
    add_rule('6', 'c', 3, True, False, 'increase')
    add_rule('6', 'c', 1, False, False, False)
    add_rule('6', 'c', 2, False, False, False)
    add_rule('6', 'c', 3, False, False, False)

    add_rule('7', 'a', 1, True, False, False)
    add_rule('7', 'a', 2, True, 'starboard', False)
    add_rule('7', 'a', 3, True, 'starboard', False)
    add_rule('7', 'a', 1, False, False, False)
    add_rule('7', 'a', 2, False, False, False)
    add_rule('7', 'a', 3, False, False, False)
    add_rule('7', 'ab', 1, True, False, False)
    add_rule('7', 'ab', 2, True, 'starboard', False)
    add_rule('7', 'ab', 3, True, 'starboard', False)
    add_rule('7', 'ab', 1, False, False, False)
    add_rule('7', 'ab', 2, False, False, False)
    add_rule('7', 'ab', 3, False, False, False)

    add_rule('7', 'b', 1, True, False, False)
    add_rule('7', 'b', 2, True, 'starboard', 'decrease')
    add_rule('7', 'b', 3, True, 'starboard', 'decrease')
    add_rule('7', 'b', 1, False, False, False)
    add_rule('7', 'b', 2, False, False, False)
    add_rule('7', 'b', 3, False, False, False)

    add_rule('7', 'c', 1, True, False, False)
    add_rule('7', 'c', 2, True, False, 'increase')
    add_rule('7', 'c', 3, True, False, 'increase')
    add_rule('7', 'c', 1, False, False, False)
    add_rule('7', 'c', 2, False, False, False)
    add_rule('7', 'c', 3, False, False, False)

    add_rule('8', 'b', 1, True, False, False)
    add_rule('8', 'b', 2, True, False, 'decrease')
    add_rule('8', 'b', 3, True, False, 'decrease')
    add_rule('8', 'b', 1, False, False, False)
    add_rule('8', 'b', 2, False, False, False)
    add_rule('8', 'b', 3, False, False, False)

    add_rule('8', 'c', 1, True, False, False)
    add_rule('8', 'c', 2, True, False, 'decrease')
    add_rule('8', 'c', 3, True, False, 'decrease')
    add_rule('8', 'c', 1, False, False, False)
    add_rule('8', 'c', 2, False, False, False)
    add_rule('8', 'c', 3, False, False, False)

    add_rule('8', 'd', 1, True, False, False)
    add_rule('8', 'd', 2, True, False, 'increase')
    add_rule('8', 'd', 3, True, False, 'increase')
    add_rule('8', 'd', 1, False, False, False)
    add_rule('8', 'd', 2, False, False, False)
    add_rule('8', 'd', 3, False, False, False)

    add_rule('9', 'c', 1, True, False, False)
    add_rule('9', 'c', 2, True, 'port', False)
    add_rule('9', 'c', 3, True, 'port', False)
    add_rule('9', 'c', 1, False, False, False)
    add_rule('9', 'c', 2, False, False, False)
    add_rule('9', 'c', 3, False, False, False)

    add_rule('9', 'd', 1, True, False, False)
    add_rule('9', 'd', 2, True, 'port', 'decrease')
    add_rule('9', 'd', 3, True, 'port', 'decrease')
    add_rule('9', 'd', 1, False, False, False)
    add_rule('9', 'd', 2, False, False, False)
    add_rule('9', 'd', 3, False, False, False)

    add_rule('9', 'e', 1, True, False, False)
    add_rule('9', 'e', 2, True, False, 'increase')
    add_rule('9', 'e', 3, True, False, 'increase')
    add_rule('9', 'e', 1, False, False, False)
    add_rule('9', 'e', 2, False, False, False)
    add_rule('9', 'e', 3, False, False, False)

    add_rule('10', 'c', 1, True, False, False)
    add_rule('10', 'c', 2, True, False, 'decrease')
    add_rule('10', 'c', 3, True, False, 'decrease')
    add_rule('10', 'c', 1, False, False, False)
    add_rule('10', 'c', 2, False, False, False)
    add_rule('10', 'c', 3, False, False, False)

    add_rule('10', 'd', 1, True, False, False)
    add_rule('10', 'd', 2, True, False, 'decrease')
    add_rule('10', 'd', 3, True, False, 'decrease')
    add_rule('10', 'd', 1, False, False, False)
    add_rule('10', 'd', 2, False, False, False)
    add_rule('10', 'd', 3, False, False, False)

    add_rule('10', 'e', 1, True, False, False)
    add_rule('10', 'e', 2, True, False, 'increase')
    add_rule('10', 'e', 3, True, False, 'increase')
    add_rule('10', 'e', 1, False, False, False)
    add_rule('10', 'e', 2, False, False, False)
    add_rule('10', 'e', 3, False, False, False)

    # Own rules
    add_rule('1', 'a', 1, False, 'starboard', False)
    add_rule('1', 'a', 2, False, False, False)
    add_rule('1', 'a', 3, False, False, False)
    add_rule('1', 'a', 1, True, 'starboard', False)
    add_rule('1', 'a', 2, True, False, False)
    add_rule('1', 'a', 3, True, False, False)

    add_rule('1b', 'a', 1, False, 'starboard', False)
    add_rule('1b', 'a', 2, False, False, False)
    add_rule('1b', 'a', 3, False, False, False)
    add_rule('1b', 'a', 1, True, 'starboard', False)
    add_rule('1b', 'a', 2, True, False, False)
    add_rule('1b', 'a', 3, True, False, False)

    add_rule('1', 'ab', 1, False, 'starboard', False)
    add_rule('1', 'ab', 2, False, False, False)
    add_rule('1', 'ab', 3, False, False, False)
    add_rule('1', 'ab', 1, True, 'starboard', False)
    add_rule('1', 'ab', 2, True, False, False)
    add_rule('1', 'ab', 3, True, False, False)

    add_rule('1b', 'ab', 1, False, 'starboard', False)
    add_rule('1b', 'ab', 2, False, False, False)
    add_rule('1b', 'ab', 3, False, False, False)
    add_rule('1b', 'ab', 1, True, 'starboard', False)
    add_rule('1b', 'ab', 2, True, False, False)
    add_rule('1b', 'ab', 3, True, False, False)

    add_rule('1', 'h', 1, False, 'starboard', False)

    add_rule('1', 'h', 1, True, 'starboard', False)

    add_rule('1b', 'h', 1, False, 'starboard', False)

    add_rule('1b', 'h', 1, True, 'starboard', False)

    add_rule('1', 'b', 1, False, 'starboard', False)

    add_rule('1', 'b', 1, True, 'starboard', False)

    add_rule('1b', 'b', 1, False, 'starboard', False)

    add_rule('1b', 'b', 1, True, 'starboard', False)

    add_rule('9', 'a', 1, False, False, False)

    add_rule('9', 'a', 1, True, False, False)

    add_rule('9', 'ab', 1, False, False, False)

    add_rule('9', 'ab', 1, True, False, False)

    add_rule('10', 'a', 1, False, False, False)

    add_rule('10', 'a', 1, True, False, False)

    add_rule('10', 'ab', 1, False, False, False)

    add_rule('10', 'ab', 1, True, False, False)

    add_rule('10', 'h', 1, False, False, False)

    add_rule('10', 'h', 1, True, False, False)

    add_rule('2', 'a', 1, False, 'port', False)
    add_rule('2', 'a', 2, False, False, False)
    add_rule('2', 'a', 3, False, False, False)
    add_rule('2', 'a', 1, True, 'port', False)
    add_rule('2', 'a', 2, True, False, False)
    add_rule('2', 'a', 3, True, False, False)

    add_rule('10', 'a', 1, False, 'starboard', False)
    add_rule('10', 'a', 2, False, False, False)
    add_rule('10', 'a', 3, False, False, False)
    add_rule('10', 'a', 1, True, 'starboard', False)
    add_rule('10', 'a', 2, True, False, False)
    add_rule('10', 'a', 3, True, False, False)

    add_rule('2', 'ab', 1, False, 'port', False)
    add_rule('2', 'ab', 2, False, False, False)
    add_rule('2', 'ab', 3, False, False, False)
    add_rule('2', 'ab', 1, True, 'port', False)
    add_rule('2', 'ab', 2, True, False, False)
    add_rule('2', 'ab', 3, True, False, False)

    add_rule('10', 'ab', 1, False, 'starboard', False)
    add_rule('10', 'ab', 2, False, False, False)
    add_rule('10', 'ab', 3, False, False, False)
    add_rule('10', 'ab', 1, True, 'starboard', False)
    add_rule('10', 'ab', 2, True, False, False)
    add_rule('10', 'ab', 3, True, False, False)

    navigation_ctrl = ctrl.ControlSystem(rules)

    return ctrl.ControlSystemSimulation(navigation_ctrl)

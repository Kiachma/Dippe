import config

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def generate_trapetzoid(start, end, buffer):
    return [(start - buffer / 2) if start > 0 else 0,
            start + buffer / 2 if start > 0 else 0,
            end - buffer / 2 if end < 360 else 360,
            (end + buffer / 2) if end < 360 else 360]
    pass


def init_fuzzy():
    # Generate universe variables

    bear = ctrl.Antecedent(np.arange(0, 360, 1), 'bearing')
    range = ctrl.Antecedent(np.arange(0, config.radius['ra']/1000, 0.5), 'range')
    rel_course = ctrl.Antecedent(np.arange(0, 360, 1), 'relative_course')
    speed_ratio = ctrl.Antecedent(np.arange(0, 10, 0.5), 'speed_ratio')
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
                                                config.radius['rvd'] / 1000 - .05,
                                                config.radius['rvd'] / 1000 + .05
                                                ])
    range['ra'] = fuzz.trapmf(range.universe, [config.radius['rvd'] / 1000 - .05,
                                               config.radius['rvd'] / 1000 + .05,
                                               config.radius['rb'] / 1000 - .05,
                                               config.radius['rb'] / 1000 + .05
                                               ])
    range['rb'] = fuzz.trapmf(range.universe, [config.radius['rb'] / 1000 - .05,
                                               config.radius['rb'] / 1000 + .05,
                                               config.radius['ra'] / 1000,
                                               config.radius['ra'] / 1000
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
    rules = []

    def add_rule(bearings, course, speed, include_rvd, course_chg, speed_chg):

        if include_rvd:
            rules.append(ctrl.Rule(
                bear[bearings] &
                rel_course[course] &
                speed_ratio[str(speed)] &
                (range['rvd']
                )
                ,
                [course_change[course_chg], speed_change[speed_chg]])
            )
        else:
            rules.append(ctrl.Rule(
                bear[bearings] &
                rel_course[course] &
                speed_ratio[str(speed)] &
                (range['rvd'] | range['ra'] | range['rb'])
                ,
                [course_change[course_chg], speed_change[speed_chg]])
            )

    add_rule('1', 'd', 1, True, 'keep', 'keep')
    add_rule('1b', 'd', 1, True, 'keep', 'keep')
    add_rule('1', 'd', 1, False, 'keep', 'keep')
    add_rule('1b', 'd', 1, False, 'keep', 'keep')

    add_rule('1', 'd', 2, True, 'keep', 'keep')
    add_rule('1b', 'd', 2, True, 'keep', 'keep')
    add_rule('1', 'd', 2, False, 'keep', 'keep')
    add_rule('1b', 'd', 2, False, 'keep', 'keep')

    add_rule('1', 'd', 3, True, 'keep', 'keep')
    add_rule('1b', 'd', 3, True, 'keep', 'keep')
    add_rule('1', 'd', 3, False, 'keep', 'keep')
    add_rule('1b', 'd', 3, False, 'keep', 'keep')

    add_rule('1', 'e', 1, True, 'starboard', 'keep')
    add_rule('1b', 'e', 1, True, 'starboard', 'keep')
    add_rule('1', 'e', 1, False, 'starboard', 'keep')
    add_rule('1b', 'e', 1, False, 'starboard', 'keep')

    add_rule('1', 'e', 2, True, 'starboard', 'keep')
    add_rule('1b', 'e', 2, True, 'starboard', 'keep')
    add_rule('1', 'e', 2, False, 'starboard', 'keep')
    add_rule('1b', 'e', 2, False, 'starboard', 'keep')

    add_rule('1', 'e', 3, True, 'starboard', 'keep')
    add_rule('1b', 'e', 3, True, 'starboard', 'keep')
    add_rule('1', 'e', 3, False, 'starboard', 'keep')
    add_rule('1b', 'e', 3, False, 'starboard', 'keep')

    add_rule('1', 'f', 1, True, 'keep', 'keep')
    add_rule('1b', 'f', 1, True, 'keep', 'keep')
    add_rule('1', 'f', 1, False, 'keep', 'keep')
    add_rule('1b', 'f', 1, False, 'keep', 'keep')

    add_rule('1', 'f', 2, True, 'keep', 'keep')
    add_rule('1b', 'f', 2, True, 'keep', 'keep')
    add_rule('1', 'f', 2, False, 'keep', 'keep')
    add_rule('1b', 'f', 2, False, 'keep', 'keep')

    add_rule('1', 'f', 3, True, 'keep', 'keep')
    add_rule('1b', 'f', 3, True, 'keep', 'keep')
    add_rule('1', 'f', 3, False, 'keep', 'keep')
    add_rule('1b', 'f', 3, False, 'keep', 'keep')

    add_rule('2', 'e', 1, True, 'keep', 'keep')
    add_rule('2', 'e', 2, True, 'keep', 'increase')
    add_rule('2', 'e', 3, True, 'keep', 'increase')
    add_rule('2', 'e', 1, False, 'keep', 'keep')
    add_rule('2', 'e', 2, False, 'keep', 'increase')
    add_rule('2', 'e', 3, False, 'keep', 'increase')

    add_rule('2', 'f', 1, True, 'keep', 'keep')
    add_rule('2', 'f', 2, True, 'starboard', 'decrease')
    add_rule('2', 'f', 3, True, 'starboard', 'decrease')
    add_rule('2', 'f', 1, False, 'keep', 'keep')
    add_rule('2', 'f', 2, False, 'starboard', 'decrease')
    add_rule('2', 'f', 3, False, 'starboard', 'decrease')

    add_rule('2', 'g', 1, True, 'keep', 'keep')
    add_rule('2', 'g', 2, True, 'starboard', 'keep')
    add_rule('2', 'g', 3, True, 'starboard', 'keep')
    add_rule('2', 'g', 1, False, 'keep', 'keep')
    add_rule('2', 'g', 2, False, 'starboard', 'keep')
    add_rule('2', 'g', 3, False, 'starboard', 'keep')

    add_rule('3', 'f', 1, True, 'keep', 'keep')
    add_rule('3', 'f', 2, True, 'keep', 'increase')
    add_rule('3', 'f', 3, True, 'keep', 'increase')
    add_rule('3', 'f', 1, False, 'keep', 'keep')
    add_rule('3', 'f', 2, False, 'keep', 'increase')
    add_rule('3', 'f', 3, False, 'keep', 'increase')

    add_rule('3', 'g', 1, True, 'keep', 'keep')
    add_rule('3', 'g', 2, True, 'keep', 'decrease')
    add_rule('3', 'g', 3, True, 'keep', 'decrease')
    add_rule('3', 'g', 1, False, 'keep', 'keep')
    add_rule('3', 'g', 2, False, 'keep', 'decrease')
    add_rule('3', 'g', 3, False, 'keep', 'decrease')

    add_rule('3', 'h', 1, True, 'keep', 'keep')
    add_rule('3', 'h', 2, True, 'keep', 'decrease')
    add_rule('3', 'h', 3, True, 'keep', 'decrease')
    add_rule('3', 'h', 1, False, 'keep', 'keep')
    add_rule('3', 'h', 2, False, 'keep', 'decrease')
    add_rule('3', 'h', 3, False, 'keep', 'decrease')

    add_rule('4', 'g', 1, True, 'keep', 'keep')
    add_rule('4', 'g', 2, True, 'keep', 'increase')
    add_rule('4', 'g', 3, True, 'keep', 'increase')
    add_rule('4', 'g', 1, False, 'keep', 'keep')
    add_rule('4', 'g', 2, False, 'keep', 'increase')
    add_rule('4', 'g', 3, False, 'keep', 'increase')

    add_rule('4', 'h', 1, True, 'keep', 'keep')
    add_rule('4', 'h', 2, True, 'port', 'decrease')
    add_rule('4', 'h', 3, True, 'port', 'decrease')
    add_rule('4', 'h', 1, False, 'keep', 'keep')
    add_rule('4', 'h', 2, False, 'port', 'decrease')
    add_rule('4', 'h', 3, False, 'port', 'decrease')

    add_rule('4', 'a', 1, True, 'keep', 'keep')
    add_rule('4', 'a', 2, True, 'port', 'decrease')
    add_rule('4', 'a', 3, True, 'port', 'decrease')
    add_rule('4', 'a', 1, False, 'keep', 'keep')
    add_rule('4', 'a', 2, False, 'port', 'decrease')
    add_rule('4', 'a', 3, False, 'port', 'decrease')
    add_rule('4', 'ab', 1, True, 'keep', 'keep')
    add_rule('4', 'ab', 2, True, 'port', 'decrease')
    add_rule('4', 'ab', 3, True, 'port', 'decrease')
    add_rule('4', 'ab', 1, False, 'keep', 'keep')
    add_rule('4', 'ab', 2, False, 'port', 'decrease')
    add_rule('4', 'ab', 3, False, 'port', 'decrease')

    add_rule('5', 'h', 1, True, 'keep', 'keep')
    add_rule('5', 'h', 2, True, 'keep', 'keep')
    add_rule('5', 'h', 3, True, 'keep', 'keep')
    add_rule('5', 'h', 1, False, 'keep', 'keep')
    add_rule('5', 'h', 2, False, 'keep', 'keep')
    add_rule('5', 'h', 3, False, 'keep', 'keep')

    add_rule('5', 'a', 1, True, 'port', 'keep')
    add_rule('5', 'a', 2, True, 'port', 'keep')
    add_rule('5', 'a', 3, True, 'port', 'keep')
    add_rule('5', 'a', 1, False, 'keep', 'keep')
    add_rule('5', 'a', 2, False, 'keep', 'keep')
    add_rule('5', 'a', 3, False, 'keep', 'keep')

    add_rule('5', 'b', 1, True, 'keep', 'keep')
    add_rule('5', 'b', 2, True, 'keep', 'keep')
    add_rule('5', 'b', 3, True, 'keep', 'keep')
    add_rule('5', 'b', 1, False, 'keep', 'keep')
    add_rule('5', 'b', 2, False, 'keep', 'keep')
    add_rule('5', 'b', 3, False, 'keep', 'keep')

    add_rule('6', 'a', 1, True, 'keep', 'keep')
    add_rule('6', 'a', 2, True, 'keep', 'decrease')
    add_rule('6', 'a', 3, True, 'keep', 'decrease')
    add_rule('6', 'a', 1, False, 'keep', 'keep')
    add_rule('6', 'a', 2, False, 'keep', 'keep')
    add_rule('6', 'a', 3, False, 'keep', 'keep')
    add_rule('6', 'ab', 1, True, 'keep', 'keep')
    add_rule('6', 'ab', 2, True, 'keep', 'decrease')
    add_rule('6', 'ab', 3, True, 'keep', 'decrease')
    add_rule('6', 'ab', 1, False, 'keep', 'keep')
    add_rule('6', 'ab', 2, False, 'keep', 'keep')
    add_rule('6', 'ab', 3, False, 'keep', 'keep')

    add_rule('6', 'b', 1, True, 'keep', 'keep')
    add_rule('6', 'b', 2, True, 'keep', 'decrease')
    add_rule('6', 'b', 3, True, 'keep', 'decrease')
    add_rule('6', 'b', 1, False, 'keep', 'keep')
    add_rule('6', 'b', 2, False, 'keep', 'keep')
    add_rule('6', 'b', 3, False, 'keep', 'keep')

    add_rule('6', 'c', 1, True, 'keep', 'keep')
    add_rule('6', 'c', 2, True, 'keep', 'increase')
    add_rule('6', 'c', 3, True, 'keep', 'increase')
    add_rule('6', 'c', 1, False, 'keep', 'keep')
    add_rule('6', 'c', 2, False, 'keep', 'keep')
    add_rule('6', 'c', 3, False, 'keep', 'keep')

    add_rule('7', 'a', 1, True, 'keep', 'keep')
    add_rule('7', 'a', 2, True, 'starboard', 'keep')
    add_rule('7', 'a', 3, True, 'starboard', 'keep')
    add_rule('7', 'a', 1, False, 'keep', 'keep')
    add_rule('7', 'a', 2, False, 'keep', 'keep')
    add_rule('7', 'a', 3, False, 'keep', 'keep')
    add_rule('7', 'ab', 1, True, 'keep', 'keep')
    add_rule('7', 'ab', 2, True, 'starboard', 'keep')
    add_rule('7', 'ab', 3, True, 'starboard', 'keep')
    add_rule('7', 'ab', 1, False, 'keep', 'keep')
    add_rule('7', 'ab', 2, False, 'keep', 'keep')
    add_rule('7', 'ab', 3, False, 'keep', 'keep')

    add_rule('7', 'b', 1, True, 'keep', 'keep')
    add_rule('7', 'b', 2, True, 'starboard', 'decrease')
    add_rule('7', 'b', 3, True, 'starboard', 'decrease')
    add_rule('7', 'b', 1, False, 'keep', 'keep')
    add_rule('7', 'b', 2, False, 'keep', 'keep')
    add_rule('7', 'b', 3, False, 'keep', 'keep')

    add_rule('7', 'c', 1, True, 'keep', 'keep')
    add_rule('7', 'c', 2, True, 'keep', 'increase')
    add_rule('7', 'c', 3, True, 'keep', 'increase')
    add_rule('7', 'c', 1, False, 'keep', 'keep')
    add_rule('7', 'c', 2, False, 'keep', 'keep')
    add_rule('7', 'c', 3, False, 'keep', 'keep')

    add_rule('8', 'b', 1, True, 'keep', 'keep')
    add_rule('8', 'b', 2, True, 'keep', 'decrease')
    add_rule('8', 'b', 3, True, 'keep', 'decrease')
    add_rule('8', 'b', 1, False, 'keep', 'keep')
    add_rule('8', 'b', 2, False, 'keep', 'keep')
    add_rule('8', 'b', 3, False, 'keep', 'keep')

    add_rule('8', 'c', 1, True, 'keep', 'keep')
    add_rule('8', 'c', 2, True, 'keep', 'decrease')
    add_rule('8', 'c', 3, True, 'keep', 'decrease')
    add_rule('8', 'c', 1, False, 'keep', 'keep')
    add_rule('8', 'c', 2, False, 'keep', 'keep')
    add_rule('8', 'c', 3, False, 'keep', 'keep')

    add_rule('8', 'd', 1, True, 'keep', 'keep')
    add_rule('8', 'd', 2, True, 'keep', 'increase')
    add_rule('8', 'd', 3, True, 'keep', 'increase')
    add_rule('8', 'd', 1, False, 'keep', 'keep')
    add_rule('8', 'd', 2, False, 'keep', 'keep')
    add_rule('8', 'd', 3, False, 'keep', 'keep')

    add_rule('9', 'c', 1, True, 'keep', 'keep')
    add_rule('9', 'c', 2, True, 'port', 'keep')
    add_rule('9', 'c', 3, True, 'port', 'keep')
    add_rule('9', 'c', 1, False, 'keep', 'keep')
    add_rule('9', 'c', 2, False, 'keep', 'keep')
    add_rule('9', 'c', 3, False, 'keep', 'keep')

    add_rule('9', 'd', 1, True, 'keep', 'keep')
    add_rule('9', 'd', 2, True, 'port', 'decrease')
    add_rule('9', 'd', 3, True, 'port', 'decrease')
    add_rule('9', 'd', 1, False, 'keep', 'keep')
    add_rule('9', 'd', 2, False, 'keep', 'keep')
    add_rule('9', 'd', 3, False, 'keep', 'keep')

    add_rule('9', 'e', 1, True, 'keep', 'keep')
    add_rule('9', 'e', 2, True, 'keep', 'increase')
    add_rule('9', 'e', 3, True, 'keep', 'increase')
    add_rule('9', 'e', 1, False, 'keep', 'keep')
    add_rule('9', 'e', 2, False, 'keep', 'keep')
    add_rule('9', 'e', 3, False, 'keep', 'keep')

    add_rule('10', 'c', 1, True, 'keep', 'keep')
    add_rule('10', 'c', 2, True, 'keep', 'decrease')
    add_rule('10', 'c', 3, True, 'keep', 'decrease')
    add_rule('10', 'c', 1, False, 'keep', 'keep')
    add_rule('10', 'c', 2, False, 'keep', 'keep')
    add_rule('10', 'c', 3, False, 'keep', 'keep')

    add_rule('10', 'd', 1, True, 'keep', 'keep')
    add_rule('10', 'd', 2, True, 'keep', 'decrease')
    add_rule('10', 'd', 3, True, 'keep', 'decrease')
    add_rule('10', 'd', 1, False, 'keep', 'keep')
    add_rule('10', 'd', 2, False, 'keep', 'keep')
    add_rule('10', 'd', 3, False, 'keep', 'keep')

    add_rule('10', 'e', 1, True, 'keep', 'keep')
    add_rule('10', 'e', 2, True, 'keep', 'increase')
    add_rule('10', 'e', 3, True, 'keep', 'increase')
    add_rule('10', 'e', 1, False, 'keep', 'keep')
    add_rule('10', 'e', 2, False, 'keep', 'keep')
    add_rule('10', 'e', 3, False, 'keep', 'keep')


    #Own rules
    add_rule('1', 'a', 1, False, 'starboard', 'keep')
    add_rule('1', 'a', 2, False, 'keep', 'keep')
    add_rule('1', 'a', 3, False, 'keep', 'keep')
    add_rule('1', 'a', 1, True, 'starboard', 'keep')
    add_rule('1', 'a', 2, True, 'keep', 'keep')
    add_rule('1', 'a', 3, True, 'keep', 'keep')

    add_rule('1b', 'a', 1, False, 'starboard', 'keep')
    add_rule('1b', 'a', 2, False, 'keep', 'keep')
    add_rule('1b', 'a', 3, False, 'keep', 'keep')
    add_rule('1b', 'a', 1, True, 'starboard', 'keep')
    add_rule('1b', 'a', 2, True, 'keep', 'keep')
    add_rule('1b', 'a', 3, True, 'keep', 'keep')

    add_rule('1', 'ab', 1, False, 'starboard', 'keep')
    add_rule('1', 'ab', 2, False, 'keep', 'keep')
    add_rule('1', 'ab', 3, False, 'keep', 'keep')
    add_rule('1', 'ab', 1, True, 'starboard', 'keep')
    add_rule('1', 'ab', 2, True, 'keep', 'keep')
    add_rule('1', 'ab', 3, True, 'keep', 'keep')

    add_rule('1b', 'ab', 1, False, 'starboard', 'keep')
    add_rule('1b', 'ab', 2, False, 'keep', 'keep')
    add_rule('1b', 'ab', 3, False, 'keep', 'keep')
    add_rule('1b', 'ab', 1, True, 'starboard', 'keep')
    add_rule('1b', 'ab', 2, True, 'keep', 'keep')
    add_rule('1b', 'ab', 3, True, 'keep', 'keep')

    add_rule('2', 'h', 1, False, 'starboard', 'keep')
    add_rule('2', 'h', 2, False, 'keep', 'keep')
    add_rule('2', 'h', 3, False, 'keep', 'keep')
    add_rule('2', 'h', 1, True, 'starboard', 'keep')
    add_rule('2', 'h', 2, True, 'keep', 'keep')
    add_rule('2', 'h', 3, True, 'keep', 'keep')

    add_rule('10', 'b', 1, False, 'port', 'keep')
    add_rule('10', 'b', 2, False, 'keep', 'keep')
    add_rule('10', 'b', 3, False, 'keep', 'keep')
    add_rule('10', 'b', 1, True, 'port', 'keep')
    add_rule('10', 'b', 2, True, 'keep', 'keep')
    add_rule('10', 'b', 3, True, 'keep', 'keep')

    navigation_ctrl = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(navigation_ctrl, flush_after_run=3 + 1)

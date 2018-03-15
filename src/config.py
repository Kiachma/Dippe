playback = dict(
    interval=1,
    rate=1

)
scale = 10
anim = True
# NM *1000
radius = dict(
    rvd=1000 / scale,
    rb=6000 / scale,
    ra=10000 / scale
)

dimensions = [-10000 / scale, 10000 / scale, -10000 / scale, 10000 / scale]
sectors = [5, 80, 10, 80, 10, 26, 54, 10, 54, 26, 5]

# bear['1'] = fuzz.trapmf(bear.universe, generate_trapetzoid(0, 5, 5))
# bear['2'] = fuzz.trapmf(bear.universe, generate_trapetzoid(5, 85, 5))
# bear['3'] = fuzz.trapmf(bear.universe, generate_trapetzoid(85, 95, 5))
# bear['4'] = fuzz.trapmf(bear.universe, generate_trapetzoid(95, 175, 5))
# bear['5'] = fuzz.trapmf(bear.universe, generate_trapetzoid(175, 185, 5))
# bear['6'] = fuzz.trapmf(bear.universe, generate_trapetzoid(185, 211, 5))
# bear['7'] = fuzz.trapmf(bear.universe, generate_trapetzoid(211, 265, 5))
# bear['8'] = fuzz.trapmf(bear.universe, generate_trapetzoid(265, 275, 5))
# bear['9'] = fuzz.trapmf(bear.universe, generate_trapetzoid(275, 329, 5))
# bear['10'] = fuzz.trapmf(bear.universe, generate_trapetzoid(329, 355, 5))
# bear['1b'] = fuzz.trapmf(bear.universe, generate_trapetzoid(355, 360, 5))
visibility = radius['ra'] / 1000
show = dict(
    visibility=False,
    sectors=False,
    arrow=True,
    paths=False,
    lights=False
)
#
# vessels = [
#     dict(id='A',
#          heading=225,
#          position=(7200 / scale, 7200 / scale),
#          speed=20,
#          max_speed=22,
#          rate_of_turn=2,
#          ap=True),
#     dict(id='B',
#          heading=135,
#          position=(-7200 / scale, 7200 / scale),
#          speed=20,
#          max_speed=22,
#          rate_of_turn=2,
#          ap=True),
#     dict(id='C',
#          heading=45,
#          position=(-7200 / scale, -7200 / scale),
#          speed=20,
#          max_speed=22,
#          rate_of_turn=2,
#          ap=True),
#     dict(id='D',
#          heading=315,
#          position=(7200 / scale, -7200 / scale),
#          speed=20,
#          max_speed=22,
#          rate_of_turn=2,
#          ap=True),
#     dict(id='E',
#          heading=225,
#          position=(5000 / scale, 5000 / scale),
#          speed=10,
#          max_speed=12,
#          rate_of_turn=3,
#          ap=True),
#     dict(id='F',
#          heading=135,
#          position=(-5000 / scale, 5000 / scale),
#          speed=10,
#          max_speed=12,
#
#          rate_of_turn=3,
#          ap=True),
#     dict(id='G',
#          heading=45,
#          position=(-5000 / scale, -5000 / scale),
#          speed=10,
#          max_speed=12,
#
#          rate_of_turn=3,
#          ap=True),
#     dict(id='H',
#          heading=315,
#          position=(5000 / scale, -5000 / scale),
#          speed=10,
#          max_speed=12,
#
#          rate_of_turn=3,
#          ap=True)
#
# ]
#

# Crossing
# vessels = [
#     dict(id='B',
#          heading=270,
#          position=(7200 / scale, 0),
#          speed=10,
#          max_speed=12,
#          rate_of_turn=3,
#          ap=True),
#     dict(id='A',
#          heading=0,
#          position=(0, -7200 / scale),
#          speed=10,
#          max_speed=12,
#          rate_of_turn=3,
#          ap=True),
#
# ]

# Head on
# vessels = [
#     dict(id='A',
#          heading=0,
#          position=(0, -7000 / scale),
#          speed=10,
#          max_speed=12,
#          rate_of_turn=2,
#          ap=True),
#     dict(id='B',
#          heading=180,
#          position=(0, 7000 / scale),
#          speed=10,
#          max_speed=12,
#          rate_of_turn=2,
#          ap=True),
# ]

# Overtake
# vessels = [
#     dict(id='A',
#          heading=0,
#          position=(0, -0),
#          speed=2,
#          max_speed=7,
#          rate_of_turn=2,
#          ap=True),
#     dict(id='B',
#          heading=0,
#          position=(0, -10000 / scale),
#          speed=10,
#          max_speed=12,
#          rate_of_turn=2,
#          ap=True),
# ]
# DIP
vessels = [
    dict(id='A',
         heading=0,
         position=(0, -4500 / scale),
         speed=5,
         max_speed=7,
         rate_of_turn=5,
         ap=True),
    dict(id='B',
         heading=203,
         position=(4500 / scale, 4500 / scale),
         speed=10,
         max_speed=13,
         rate_of_turn=5,
         ap=True),
]

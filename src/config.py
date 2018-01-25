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
sectors = dict(
    headOn=[337.5, 22.5],
    crossing_give_way=(0, 112.5),
    crossing_stand_on=(247.5, 360),
    over_take_give_way=(337.5, 22.5),
    over_take_stand_on=(112.5, 247.5)
)
visibility = radius['ra'] / 1000
show = dict(
    visibility=False,
    sectors=True,
    arrow=True,
    paths=False,
    lights=False
)
#
# vessels = [
#     dict(id='A',
#          heading=225,
#          position=(7200/scale, 7200/scale),
#          speed=20,
#          rate_of_turn=2,
#          ap=True),
#     dict(id='B',
#          heading=135,
#          position=(-7200/scale, 7200/scale),
#          speed=20,
#          rate_of_turn=2,
#          ap=True),
#     dict(id='C',
#          heading=45,
#          position=(-7200/scale, -7200/scale),
#          speed=20,
#          rate_of_turn=2,
#          ap=True),
#     dict(id='D',
#          heading=315,
#          position=(7200/scale, -7200/scale),
#          speed=20,
#          rate_of_turn=2,
#          ap=False),
#     dict(id='E',
#          heading=225,
#          position=(5000/scale, 5000/scale),
#          speed=10,
#          rate_of_turn=3,
#          ap=True),
#     dict(id='F',
#          heading=135,
#          position=(-5000/scale, 5000/scale),
#          speed=10,
#          rate_of_turn=3,
#          ap=True),
#     dict(id='G',
#          heading=45,
#          position=(-5000/scale, -5000/scale),
#          speed=10,
#          rate_of_turn=3,
#          ap=True),
#     dict(id='H',
#          heading=315,
#          position=(5000/scale, -5000/scale),
#          speed=10,
#          rate_of_turn=3,
#          ap=True)
#
# ]
#

# # Crossing
# vessels = [
#     dict(id='A',
#          heading=0,
#          position=(0, -7200 / scale),
#          speed=20,
#          rate_of_turn=3,
#          ap=True),
#     dict(id='B',
#          heading=90,
#          position=(-7200 / scale, 0),
#          speed=20,
#          rate_of_turn=3,
#          ap=True),
# ]

# Head on
# vessels = [
#     dict(id='A',
#          heading=0,
#          position=(0, -7000/scale),
#          speed=10,
#          rate_of_turn=2,
#          ap=True),
#     dict(id='B',
#          heading=180,
#          position=(0, 7000/scale),
#          speed=10,
#          rate_of_turn=2,
#          ap=False),
# ]

# Overtake
vessels = [
    dict(id='A',
         heading=0,
         position=(0, -0),
         speed=5 ,
         rate_of_turn=2,
         ap=True),
    dict(id='B',
         heading=0,
         position=(0, -10000/scale),
         speed=10 ,
         rate_of_turn=2,
         ap=True),
]

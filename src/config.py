playback = dict(
    interval=1000,
    rate=1
)
opra = dict(
    granularity=4
)
visibility = 400
dimensions = [-250, 250, -250, 250]
sectors = dict(
    headOn=[337.5, 22.5],
    crossing_give_way=(0, 112.5),
    crossing_stand_on=(247.5, 360),
    over_take_give_way=(337.5, 22.5),
    over_take_stand_on=(112.5, 247.5)
)

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
#          position=(150, 150),
#          speed=10,
#          rate_of_turn=2),
#     dict(id='B',
#          heading=135,
#          position=(-150, 150),
#          speed=10,
#          rate_of_turn=2),
#     dict(id='C',
#          heading=45,
#          position=(-150, -150),
#          speed=10,
#          rate_of_turn=2),
#     dict(id='D',
#          heading=315,
#          position=(150, -150),
#          speed=10,
#          rate_of_turn=2),
#     dict(id='E',
#          heading=225,
#          position=(300, 300),
#          speed=20,
#          rate_of_turn=3),
#     dict(id='F',
#          heading=135,
#          position=(-300, 300),
#          speed=20,
#          rate_of_turn=3),
#     dict(id='G',
#          heading=45,
#          position=(-300, -300),
#          speed=20,
#          rate_of_turn=3),
#     dict(id='H',
#          heading=315,
#          position=(300, -300),
#          speed=20,
#          rate_of_turn=3)
#
# ]
#

# # Crossing
# vessels = [
#     dict(id='A',
#          heading=0,
#          position=(0, -250),
#          speed=20,
#          rate_of_turn=3),
#     dict(id='B',
#          heading=90,
#          position=(-250, 0),
#          speed=20,
#          rate_of_turn=3),
# ]

# Head on
vessels = [
    dict(id='A',
         heading=0,
         position=(0, -250),
         speed=20,
         rate_of_turn=2),
    dict(id='B',
         heading=180,
         position=(0, 250),
         speed=20,
         rate_of_turn=2),
]

# Overtake
# vessels = [
#     dict(id='A',
#          heading=0,
#          position=(0, -200),
#          speed=10,
#          rate_of_turn=2),
#     dict(id='B',
#          heading=0,
#          position=(0, -400),
#          speed=20,
#          rate_of_turn=2),
# ]

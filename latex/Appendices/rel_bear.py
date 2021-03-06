def theta_to_nav(theta):
    heading = theta + 90
    heading = heading - theta * 2
    if heading > 360:
        heading = heading - 360
    elif heading < 0:
        heading = heading + 360
    return heading

def compass_to_relative(compass, heading):
    x = compass - heading
    if x < 0:
        return x + 360
    else:
        return x

def calculate_initial_compass_bearing(pointA, pointB):
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")
    if pointB[0] > pointA[0]:
        x_diff = abs(pointA[0] - pointB[0])
    else:
        x_diff = -abs(pointA[0] - pointB[0])

    if pointB[1] > pointA[1]:
        y_diff = abs(pointA[1] - pointB[1])
    else:
        y_diff = -abs(pointA[1] - pointB[1])

    initial_bearing = math.atan2(y_diff, x_diff)

    initial_bearing = math.degrees(initial_bearing)
    initial_bearing = theta_to_nav(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

def cartesian_coords_to_compass(main_vessel, observed_vessel):
    main_observed = calculate_initial_compass_bearing(
        (main_vessel.position.x
        main_vessel.position.y),
        (observed_vessel.position.x,
        observed_vessel.position.y))

    return main_observed

def cartesian_coords_to_relative(main_vessel, observed_vessel):
    main_observed= cartesian_coords_to_compass(main_vessel,
     observed_vessel)

    main_observed = compass_to_relative(main_observed,
     main_vessel.heading)

    return main_observed
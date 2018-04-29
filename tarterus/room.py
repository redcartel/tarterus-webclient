from tarterus.maparray import MapArray
from tarterus.graphpaper import back, turn_positive, right, left
from tarterus.graphpaper import advance  # turn_across, empty, middle_value
from tarterus.graphpaper import is_positive, gt_or_eq
# from random import randint

DICE_ARRAY = [15, 10, 10]
EXIT_DICE_ARRAY = [10, 20, 20]

DONT_OVERLAP_SQUARES = ['room', 'hall', 'stup', 'sdwn']


def no_overlap(squares, checked=None):
    global DONT_OVERLAP_SQUARES
    if checked is None:
        checked = DONT_OVERLAP_SQUARES

    if checked == 'all':
        return all(s[0] == 'void' for s in squares)

    def not_overlap(msquare):
        if msquare[0] not in checked:
            return True

    return all(not_overlap(s) for s in squares)


def rect_fits(maparray, x, y, w, h, checked=None):
    if x <= 0 or y <= 0:
        return False
    if x + w >= maparray.w or y + h >= maparray.h:
        return False
    return no_overlap(maparray[x:x+w, y:y+h].squares(), checked)


def room(w, h, rsquare):
    rnum = rsquare[1]
    room = MapArray(rsquare, (w, h))
    room[0:w:w-1, 1:h-1] = ('vwal', rnum)
    room[1:w-1, 0:h:h-1] = ('hwal', rnum)
    room[0:w:w-1, 0] = ('tcor', rnum)
    room[0:w:w-1, h-1] = ('bcor', rnum)
    return room


def draw_room(engine, x, y, w, h, rsquare):
    engine.log("draw_room {}, {}, {}, {}".format(x, y, w, h))
    # if rect_fits(maparray, x, y, w, h):
    r = room(w, h, rsquare)
    # preserve corner tiles for overlapping rooms
    for x0 in range(x, x+w):
        for y0 in range(y, y+h):
            if r[x0-x, y0-y][0] == 'tcor':
                engine.maparray[x0, y0] = r[x0-x, y0-y]
            elif engine.maparray[x0, y0][0] not in ['tcor', 'bcor']:
                engine.maparray[x0, y0] = r[x0-x, y0-y]
    # engine.maparray[x:x+w, y:y+h] = room(w, h, rsquare)
    # return True
    # else:
    # return False


def draw_room_at_entrance(maparray, x, y, direction, w, h, offset):
    pass


# find_loc(maparray, x, y, w, h, direction, width, dice
# Find the x & y coordinates that place a room originating from a given door
# or passage location without overlapping prohibited squares or fitting
# incorrectly with a multi-tile entrance
# Search begins at at -offset-1 squares from the origin along the direction
# orthogonal to the entrance direction. where initial offset is
# 2d10-11 + (width-2)//2 over %(width-2)
# (note this means currently the algorithm will not do a complete search for
# rooms with an orthogonal dimension greater than 20 squares (90 feet internal
# dimension) which is cool for the 5e DMG tables, but should be expanded for
# future variety of algorithms
# (TODO: variable number of d10s? use d20s?, I  like the pseudo-normal
# distribution of multiple dice)
# An assumption is a multi-tile entrance will be no wider than the originating
# wall's dimension -(squares occupied by corners & perpendicular walls.
# current max passage width is 40ft (8 tiles) which is larger than the smallest
# rooms on the table. Current way to solve this is to step up the room sizes
# until one fits. Handled in dispatch
#
# params:
# x, y  : location of entrance (located on one of the room's walls)
# w, h  : dimensions of room including the enclosing walls
# direction : the direction of the entrance (entering heading east etc.)
# width : the width of the entrance, 1 for a door, possibly multi for open
# passage
# TODO: more literate code, this is a head-scratcher for sure
# TODO: rewirte this, it fails to check at end_offset and should check in a
# random direction.
def find_loc(maparray, x, y, w, h, direction, width, dice, checked=None):
    # size of dimension orthogonal to the direction & dimen. in direction
    o_length, d_length = w, h
    if direction in ["e", "w"]:
        o_length, d_length = h, w

    d_sum = dice[0] + dice[1] - 11
    base_offset = d_sum + ((o_length - 2) // 2)
    offset = base_offset % (o_length - 2)
    end_offset = (offset - 1) % (o_length - 2)
    o_direction = turn_positive(direction)
    while offset != end_offset:
        # find room x,y location after moved by offset
        x0, y0 = x, y
        x0, y0 = advance(x0, y0, back(o_direction), offset + 1)
        # print(x, y, offset + 1, x0, y0)
        if not is_positive(direction):
            x0, y0 = advance(x0, y0, direction, d_length - 1)
# advance offset
        base_offset = base_offset + 1
        offset = base_offset % (o_length - 2)

# now account for bounds established by entrance width
# dummy values pass check
        x1, y1, x2, y2 = (2, 2, 0, 0)
        if width > 1:
            x1, y1 = advance(x0, y0, o_direction, o_length - 1)
            x2, y2 = advance(x, y, o_direction, width - 1)
        if gt_or_eq((x2, y2), (x1, y1), o_direction):
            pass
        elif not rect_fits(maparray, x0, y0, w, h, checked):
            pass
        else:
            return x0, y0
    return False, False


def place_entrance(engine, origin, x, y, direction, width, psquare, dice):
    engine.log(":: Place_entrance\n\t{}, {}, {}, width: {}".
               format(x, y, direction, width))
    # if origin == "door":
    #     engine.maparray[x, y] = ('door', psquare[1])
    if origin == "passage":
        if direction in ["e", "w"]:
            engine.maparray[x, y: y+width] = ('open', psquare[1])
        elif direction in ["n", "s"]:
            engine.maparray[x: x+width, y] = ('open', psquare[1])


# Tables. Currently does not handle over-wide passage entrances well
# TODO: wide passages
# 20 x 20 room
def room_table_1_2(engine, origin, x, y, direction, width, rsquare, dice):
    engine.log(":: room1_2")
    x0, y0 = find_loc(engine.maparray, x, y, 6, 6, direction, width, dice)
    if x0 is not False:
        draw_room(engine, x0, y0, 6, 6, rsquare)
        engine.add(["exit", {"x": x0, "y": y0, "w": 6, "h": 6, "num": -1,
                             "big": False, "direction": direction}])
        place_entrance(engine, origin, x, y,
                       direction, width, rsquare, dice)
        engine.log("\tpassed")
        return (True,)
    else:
        engine.log("\tfailed")
        return (False,)


# 30 x 30 room
def room_table_3_4(engine, origin, x, y, direction, width, rsquare, dice):
    x0, y0 = find_loc(engine.maparray, x, y, 8, 8, direction, width, dice)
    if x0 is not False:
        draw_room(engine, x0, y0, 8, 8, rsquare)
        engine.add(["exit", {"x": x0, "y": y0, "w": 8, "h": 8, "num": -1,
                             "big": False, "direction": direction}])
        place_entrance(engine, origin, x, y,
                       direction, width, rsquare, dice)
        return (True,)
    else:
        return room_table_1_2(engine, origin, x, y,
                              direction, width, rsquare, dice)


# 40 x 40 room
def room_table_5_6(engine, origin, x, y, direction, width, rsquare, dice):
    x0, y0 = find_loc(engine.maparray, x, y, 10, 10, direction, width, dice)
    if x0 is not False:
        draw_room(engine, x0, y0, 10, 10, rsquare)
        engine.add(["exit", {"x": x0, "y": y0, "w": 10, "h": 10, "num": -1,
                             "big": False, "direction": direction}])
        place_entrance(engine, origin, x, y,
                       direction, width, rsquare, dice)
        return (True,)
    else:
        return room_table_3_4(engine, origin, x, y,
                              direction, width, rsquare, dice)


# 20 x 30 room
def room_table_7_9(engine, origin, x, y, direction, width, rsquare, dice):
    a, b = 6, 8
    if dice[0] % 2 == 0:
        a, b = b, a

    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        draw_room(engine, x0, y0, a, b, rsquare)
        engine.add(["exit", {"x": x0, "y": y0, "w": a, "h": b, "num": -1,
                             "big": False, "direction": direction}])
        place_entrance(engine, origin, x, y,
                       direction, width, rsquare, dice)
        return (True,)

    a, b = b, a
    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        draw_room(engine, x0, y0, a, b, rsquare)
        engine.add(["exit", {"x": x0, "y": y0, "w": a, "h": b, "num": -1,
                             "big": False, "direction": direction}])
        place_entrance(engine, origin, x, y,
                       direction, width, rsquare, dice)
        return (True,)

    return room_table_1_2(engine, origin, x, y, direction,
                          width, rsquare, dice)


# 30 x 40 room
def room_table_10_12(engine, origin, x, y, direction, width, rsquare, dice):
    a, b = 8, 10
    if dice[0] % 2 == 0:
        a, b = b, a
    engine.log("room_table_10_12")
    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    engine.log("x0:{} y0:{} ".format(x0, y0))
    if x0 is not False:
        engine.log("first try")
        draw_room(engine, x0, y0, a, b, rsquare)
        engine.add(["exit", {"x": x0, "y": y0, "w": a, "h": b, "num": -1,
                             "big": False, "direction": direction}])
        place_entrance(engine, origin, x, y,
                       direction, width, rsquare, dice)
        return (True,)

    a, b = b, a
    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    engine.log("x0:{} y0:{} ".format(x0, y0))
    if x0 is not False:
        engine.log("second try")
        draw_room(engine, x0, y0, a, b, rsquare)
        engine.add(["exit", {"x": x0, "y": y0, "w": a, "h": b, "num": -1,
                             "big": False, "direction": direction}])
        place_entrance(engine, origin, x, y,
                       direction, width, rsquare, dice)
        return (True,)
    engine.log("fail to 7_9")
    return room_table_7_9(engine, origin, x, y, direction,
                          width, rsquare, dice)


# 40 x 50 room
def room_table_13_14(engine, origin, x, y, direction, width, rsquare, dice):
    a, b = 10, 12
    if dice[0] % 2 == 0:
        a, b = b, a
    engine.log("room_table_13_14")
    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    engine.log("x0:{} y0:{} ".format(x0, y0))
    if x0 is not False:
        engine.log("first try")
        draw_room(engine, x0, y0, a, b, rsquare)
        engine.add(["exit", {"x": x0, "y": y0, "w": a, "h": b, "num": -1,
                             "big": True, "direction": direction}])
        place_entrance(engine, origin, x, y,
                       direction, width, rsquare, dice)
        return (True,)

    a, b = b, a
    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    engine.log("x0:{} y:{} ".format(x0, y0))
    if x0 is not False:
        engine.log("second try")
        draw_room(engine, x0, y0, a, b, rsquare)
        engine.add(["exit", {"x": x0, "y": y0, "w": a, "h": b, "num": -1,
                             "big": True, "direction": direction}])
        place_entrance(engine, origin, x, y,
                       direction, width, rsquare, dice)
        return (True,)
    engine.log("fail to 10_12")
    return room_table_10_12(engine, origin, x, y, direction,
                            width, rsquare, dice)


# 50 x 80 room
def room_table_15(engine, origin, x, y, direction, width, rsquare, dice):
    a, b = 12, 18
    if dice[0] % 2 == 0:
        a, b = b, a

    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        draw_room(engine, x0, y0, a, b, rsquare)
        engine.add(["exit", {"x": x0, "y": y0, "w": a, "h": b, "num": -1,
                             "big": True, "direction": direction}])
        place_entrance(engine, origin, x, y,
                       direction, width, rsquare, dice)
        return (True,)

    a, b = b, a
    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        draw_room(engine, x0, y0, a, b, rsquare)
        engine.add(["exit", {"x": x0, "y": y0, "w": a, "h": b, "num": -1,
                             "big": True, "direction": direction}])
        place_entrance(engine, origin, x, y,
                       direction, width, rsquare, dice)
        return (True,)

    return room_table_13_14(engine, origin, x, y, direction,
                            width, rsquare, dice)


# NOTE: irregular behavior if passages can have width greater than 8(40 ft)
# (40 ft)
def dispatch_room(engine, element, dice):
    x = element[2]
    y = element[3]
    origin = element[1]
    direction = element[4]
    width = element[5]
    rsquare = element[6]
    die_roll = dice[0]
    dice = dice[1:]
    # bit of a hack, width is (w, h) tuple
    if origin == "draw":
        draw_room(engine, x, y, *width, rsquare)
    elif die_roll <= 2:
        # 20x20
        if width <= 4:
            return room_table_1_2(engine, origin, x, y, direction,
                                  width, rsquare, dice)
        elif width <= 6:
            return room_table_3_4(engine, origin, x, y, direction,
                                  width, rsquare, dice)
        elif width <= 8:
            return room_table_5_6(engine, origin, x, y, direction,
                                  width, rsquare, dice)
    elif die_roll <= 4:
        # 30x30
        if width <= 6:
            return room_table_3_4(engine, origin, x, y, direction,
                                  width, rsquare, dice)
        elif width <= 8:
            return room_table_5_6(engine, origin, x, y, direction,
                                  width, rsquare, dice)
    elif die_roll <= 6:
        # 40x40
        return room_table_5_6(engine, origin, x, y,
                              direction, width, rsquare, dice)
    elif die_roll <= 9:
        # 20x30
        if width <= 6:
            return room_table_7_9(engine, origin, x, y, direction,
                                  width, rsquare, dice)
        elif width <= 8:
            return room_table_10_12(engine, origin, x, y, direction,
                                    width, rsquare, dice)
    elif die_roll <= 12:
        # 30x40
        return room_table_10_12(engine, origin, x, y,
                                direction, width, rsquare, dice)
    elif die_roll <= 14:
        # 40x50
        return room_table_13_14(engine, origin, x, y,
                                direction, width, rsquare, dice)
    elif die_roll <= 15:
        # 50x80
        return room_table_15(engine, origin, x, y,
                             direction, width, rsquare, dice)


def valid_exit(engine, x, y, direction):
    if direction in ["e", "w"] and engine.maparray[x, y][0] != 'vwal':
        return False

    elif direction in ["n", "s"] and engine.maparray[x, y][0] != 'hwal':
        return False

    x0, y0 = advance(x, y, direction, 1)
    sq = engine.maparray[x0, y0][0]
    if sq not in ['void', 'hall', 'room', 'vwal']:
        return False

    x1, y1 = advance(x, y, right(direction), 1)
    x2, y2 = advance(x, y, left(direction), 1)
    sq1 = engine.maparray[x1, y1][0]
    sq2 = engine.maparray[x2, y2][0]
    if sq1 in ["door", "open"] or sq2 in ["door", "open"]:
        return False

    return True


def find_single_exit_square(engine, x, y, w, h, direction, dice):
    if direction in ["e", "w"]:
        dimension = w
        o_dimension = h
    else:
        dimension = h
        o_dimension = w

    x0, y0 = x, y
    if is_positive(direction):
        x0, y0 = advance(x0, y0, direction, dimension - 1)

    x0, y0 = advance(x0, y0, turn_positive(direction), 1)
    engine.log("::find_single_exit_square\n\tchecking {}, {}, {} for {}".
               format(x0, y0, direction, o_dimension))

    _range = (0, o_dimension, 1)
    if dice[1] % 2 == 1:
        _range = (o_dimension - 1, -1, -1)

    offset = dice[0]
    n = 0
    for n in _range:
        place = (n + offset) % o_dimension
        x1, y1 = advance(x0, y0, turn_positive(direction), place)
        if valid_exit(engine, x1, y1, direction):
            return x1, y1

    return False, False


def num_exit_table(die, big):
    if big is True:
        if die <= 3:
            return 0
        elif die <= 8:
            return 1
        elif die <= 13:
            return 2
        elif die <= 17:
            return 3
        elif die <= 18:
            return 4
        elif die <= 19:
            return 5
        elif die <= 20:
            return 6
    else:
        if die <= 5:
            return 0
        if die <= 11:
            return 1
        if die <= 15:
            return 2
        if die <= 18:
            return 3
        if die <= 20:
            return 4


def exit_wall_table(die, direction):
    if die <= 7:
        return direction
    elif die <= 12:
        return left(direction)
    elif die <= 17:
        return right(direction)
    elif die <= 20:
        return back(direction)


def exit_door(engine, x, y, w, h, direction, num, big, dice):
    engine.log(":: exit_door")
    if num == -1:
        num = num_exit_table(dice[0], big)
        engine.log("\tnum rolled = {}".format(num))

    e_dir = exit_wall_table(dice[1], direction)

    x0, y0 = find_single_exit_square(engine, x, y, w, h, e_dir, dice)
    engine.log("\tfind_single_exit_square on {}: {}".format(e_dir, (x0, y0)))
    if x0 is not False:
        engine.add(["door", "exit", x0, y0, e_dir, 1, ("door", -1)])

    if num > 1:
        engine.add(["exit", {
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "num": num - 1,
            "big": big,
            "direction": direction
            }])

    return (True,)


def dispatch_exit(engine, element, dice):
    x = element[1]["x"]
    y = element[1]["y"]
    w = element[1]["w"]
    h = element[1]["h"]
    num = element[1]["num"]
    big = element[1]["big"]
    direction = element[1]["direction"]
    die = dice[0]
    dice = dice[1:]
    if num != -1 and num <= 0:
        return (True,)

    if die <= 10:
        return exit_door(engine, x, y, w, h, direction, num, big, dice)

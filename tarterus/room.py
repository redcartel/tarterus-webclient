from tarterus.maparray import MapArray
from tarterus.graphpaper import back, turn_positive, right, left
from tarterus.graphpaper import advance  # turn_across, empty, middle_value
from tarterus.graphpaper import is_positive, gt_or_eq, distance
from tarterus.passage import passage_width_table
# from random import randint

DICE_ARRAY = [15, 10, 10]
EXIT_DICE_ARRAY = [20, 20, 20]

DONT_OVERLAP_SQUARES = ['room', 'hall', 'stup', 'sdwn', 'open']


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
            # always draw top corners from the new room
            undersquare = engine.maparray[x0, y0]
            if r[x0-x, y0-y][0] == 'tcor':
                engine.maparray[x0, y0] = r[x0-x, y0-y]
            # bottom corners become top corners if overwriting vertical wall
            elif r[x0-x, y0-y][0] == 'bcor' and undersquare[0] == 'vwal':
                engine.maparray[x0, y0] = ('tcor', rsquare[1])
            # otherwise don't draw over existing corners
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
        engine.describe(rsquare[1], {"w": 20, "h": 20})
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
        engine.describe(rsquare[1], {"w": 30, "h": 30})
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
        engine.describe(rsquare[1], {"w": 40, "h": 40})
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
        engine.describe(rsquare[1], {"w": (a-2)*5, "h": (b-2)*5})
        return (True,)

    a, b = b, a
    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        draw_room(engine, x0, y0, a, b, rsquare)
        engine.add(["exit", {"x": x0, "y": y0, "w": a, "h": b, "num": -1,
                             "big": False, "direction": direction}])
        place_entrance(engine, origin, x, y,
                       direction, width, rsquare, dice)
        engine.describe(rsquare[1], {"w": (a-2)*5, "h": (b-2)*5})

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
        engine.describe(rsquare[1], {"w": (a-2)*5, "h": (b-2)*5})
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
        engine.describe(rsquare[1], {"w": (a-2)*5, "h": (b-2)*5})
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
        engine.describe(rsquare[1], {"w": (a-2)*5, "h": (b-2)*5})
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
        engine.describe(rsquare[1], {"w": (a-2)*5, "h": (b-2)*5})
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
        engine.describe(rsquare[1], {"w": (a-2)*5, "h": (b-2)*5})
        return (True,)

    a, b = b, a
    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        draw_room(engine, x0, y0, a, b, rsquare)
        engine.add(["exit", {"x": x0, "y": y0, "w": a, "h": b, "num": -1,
                             "big": True, "direction": direction}])
        place_entrance(engine, origin, x, y,
                       direction, width, rsquare, dice)
        engine.describe(rsquare[1], {"w": (a-2)*5, "h": (b-2)*5})
        return (True,)

    return room_table_13_14(engine, origin, x, y, direction,
                            width, rsquare, dice)


# TODO: weird room shapes

# NOTE: irregular behavior if passages can have width greater than 8(40 ft)
# (40 ft)
def dispatch_room(engine, element, dice):
    x = element[2]
    y = element[3]
    origin = element[1]
    direction = element[4]
    width = element[5]
    rsquare = element[6]
    if rsquare[1] == -1:
        rsquare = engine.generate_description(rsquare)
        engine.describe(rsquare[1], {"type": "chamber", "w": 0, "h": 0})
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

    _range = (0, o_dimension-2, 1)
    if dice[1] % 2 == 1:
        _range = (o_dimension-3, -1, -1)

    offset = dice[0]
    n = 0
    for n in _range:
        place = (n + offset) % o_dimension
        x1, y1 = advance(x0, y0, turn_positive(direction), place)
        if valid_exit(engine, x1, y1, direction):
            return x1, y1

    return False, False


def find_exit_range(engine, x, y, w, h, direction, dice):
    x0, y0 = find_single_exit_square(engine, x, y, w, h, direction, dice)
    if x0 is False:
        return False, False, False
    x1, y1 = x0, y0
    px, py, nx, ny = None, None, None, None
    # find positive most square in range
    while valid_exit(engine, x1, y1, direction):
        px, py = x1, y1
        x1, y1 = advance(x1, y1, turn_positive(direction), 1)

    # find negative most square in range
    x1, y1 = x0, y0
    while valid_exit(engine, x1, y1, direction):
        nx, ny = x1, y1
        x1, y1 = advance(x1, y1, back(turn_positive(direction)), 1)

    return (nx, ny, distance((nx, ny), (px, py)))


def find_exit_passage(engine, x, y, w, h, direction, dice):
    x0, y0, width = find_exit_range(engine, x, y, w, h, direction, dice)
    if x0 is False:
        return False, False, False
    width0 = passage_width_table(dice[0])['width']
    while width0 > width:
        if width0 > 2:
            width0 = width0 - 2
        else:
            width0 = width0 - 1

    offset = dice[1]
    if dice[0] % 2 == 0:
        _range = range(0, width)
    else:
        _range = range(width-1, -1, -1)
    for i in _range:
        d = (i + offset) % width
        if d + width0 <= width:
            x1, y1 = advance(x0, y0, turn_positive(direction), d)
            return x1, y1, width0
    return False, False, False


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


def exit_table_11_20(engine, x, y, w, h, direction, num, big, dice):
    engine.log(":: exit_passage")
    if num == -1:
        num = num_exit_table(dice[0], big)

    e_dir = exit_wall_table(dice[1], direction)
    x0, y0, width = find_exit_passage(engine, x, y, w, h, e_dir, dice)
    if x0 is False:
        return (False,)

    x1, y1 = advance(x0, y0, e_dir, 1)
    sq = engine.maparray[x, y]
    engine.add(["hall", "exit", x1, y1, e_dir, width, ("hall", -1)])

    for i in range(width):
        x2, y2 = advance(x0, y0, turn_positive(e_dir), i)
        engine.maparray[x2, y2] = ('open', sq[1])

    return (True,)


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
    elif die <= 20:
        return exit_table_11_20(engine, x, y, w, h, direction, num, big, dice)


def describe_chamber(engine, d):
    dice = engine.roll([100, 100])
    chamber_type = general_chamber(dice[0])
    ret = "<p>A {} foot by {} foot {}.</p>".\
          format(d['w'], d['h'], chamber_type)
    contents = chamber_contents(engine, dice[1])
    ret += contents
    return ret


def chamber_contents(engine, die=0):
    die = engine.roll([100])[0]
    if die <= 8:
        return "<p>monsters: " + chamber_monster(engine) + "</p>"
    elif die <= 15:
        return "<p>monsters: {} with {}.</p>".format(
                chamber_monster(engine), which_treasure(engine))
    elif die <= 27:
        return "<p>monsters: {}.</p>".format(
                chamber_monster(engine))
    elif die <= 33:
        return "<p>monsters: {} guarding {}.</p>".format(
                chamber_monster(engine), which_treasure(engine))
    elif die <= 42:
        return "<p>monsters: {}.</p>"
    elif die <= 50:
        return "<p>monsters {} with {}.</p>".format(
                chamber_monster(engine), which_treasure(engine))
    elif die <= 58:
        return "<p>" + chamber_hazard() + " and " + treasure(engine) + "</p>"
    elif die <= 63:
        return "<p>" + chamber_obstacle() + "</p>"
    elif die <= 73:
        return "<p>" + chamber_trap() + "</p>"
    elif die <= 76:
        return "<p>" + chamber_trap() + " protecting " +\
                which_treasure(engine) + "</p>"
    elif die <= 80:
        return "<p>" + chamber_trick() + "</p>"
    elif die <= 88:
        return "<p> This is an otherwise empty room </p>"
    elif die <= 94:
        return "<p>" + chamber_hazard() + "</p>"
    elif die <= 100:
        return "<p>" + which_treasure(engine) + "</p>"


def which_treasure(engine):
    dice = engine.roll([20])
    if dice[0] <= 18:
        return treasure(engine)
    elif dice[0] <= 20:
        return horde(engine)


def chamber_hazard():
    return "a hazard!"


def chamber_obstacle():
    return "an obstacle!"


def chamber_trap():
    return "a trap!"


def chamber_trick():
    return "a trick!"


def chamber_monster(engine):
    dice = engine.roll([100, 20])
    if die <= 1:
        return "1 mind flayer arcanist"
    elif die <= 2:
        n = sum(engine.roll([3])) + 1
        return "{} giant poisonous snakes".format(n)
    elif die <= 3:
        n = sum(engine.roll([3]))
        return "{} giant lizards".format(n)
    elif die <= 4:
        n = sum(engine.roll([4, 4]))
        return "{} giant fire beetles".format(n)
    elif die <= 5:
        n = sum(engine.roll([8])) + 1
        return "{} flumphs".format(n)
    elif die <= 6:
        return "1 shrieker"
    elif die <= 7:
        n = sum(engine.roll([12]))
        return "{} giant rats".format(n)
    elif die <= 8:
        n = sum(engine.roll([4, 4]))
        return "{} kobolds".format(n)
    elif die <= 9:
        n = sum(engine.roll([8])) + 1
        return "{} stirges".format(n)
    elif die <= 10:
        n = sum(engine.roll([4, 4]))
        return "{} human tribal warriors fleeing the dungeon".format(n)
    elif die <= 12:
        n = sum(engine.roll([10]))
        return "{} troglodytes".format(n)
    elif die <= 14:
        n = sum(engine.roll([2]))
        return "{} gray oozes".format(n)
    elif die <= 16:
        n = sum(engine.roll([6, 6, 6]))
        return "{} stirges".format(n)
    elif die <= 18:
        n = sum(engine.roll([3]))
        return "{} magma mephits".format(n)
    elif die <= 20:
        n = sum(engine.roll([10]))
        return "{} goblins".format(n)
    elif die <= 22:
        return "graffiti left by some rude orcs"
    elif die <= 24:
        return "1 insect swarm"
    elif die <= 25:
        return "1 deep gnome"
    elif die <= 28:
        n = sum(engine.roll([8]))+1
        return "{} drow".format(n)
    elif die <= 30:
        n = sum(engine.roll([4]))
        return "{} violet fungi".format(n)
    elif die <= 32:
        n = sum(engine.roll([12]))
        return "{} kuo-toa".format(n)
    elif die <= 33:
        return "1 rust monster"
    elif die <= 35:
        return "a rubble strewn passageway that appears to have been cleared\
from a recent cave-in"
    elif die <= 37:
        n = sum(engine.roll([8])) + 1
        return "{} giant bats".format(n)
    elif die <= 39:
        n = sum(engine.roll([6, 6, 6]))
        return "{} kobolds".format(n)
    elif die <= 41:
        n = sum(engine.roll([4, 4]))
        return "{} grimlocks".format(n)
    elif die <= 43:
        n = sum(engine.roll([4])) + 3
        return "{} swarms of bats".format(n)
    elif die <= 44:
        return "one dwarf prospector (a scout) looking for gold"
    elif die <= 45:
        if dice[1] % 2 == 0:
            return "1 carrion crawler"
        else:
            return "1 gelatinous cube"
    elif die <= 46:
        if dice[1] % 2 == 0:
            n = sum(engine.roll([8]))
            return "{} darkmantles".format(n)
        else:
            n = sum(engine.roll([4, 4]))
            return "{} piercers".format(n)
    elif die <= 47:
        return "one hell hound"
    elif die <= 48:
        n = sum(engine.roll([3]))
        return "{} specters".format(n)
    elif die <= 49:
        n = sum(engine.roll([4]))
        return "{} bugbears".format(n)
    elif die <= 50:
        n = sum(engine.roll([10])) + 5
        return "{} winged kobolds".format(n)
    elif die <= 51:
        n = sum(engine.roll([4]))
        return "{} fire snakes".format(n)
    elif die <= 52:
        n = sum(engine.roll([8, 8])) + 1
        return "{} troglodytes".format(n)
    elif die <= 53:
        n = sum(engine.roll([6]))
        return "{} giant spiders".format(n)
    elif die <= 54:
        n = sum(engine.roll([6, 6, 6]))
        return "{} kuo-toa".format(n)
    elif die <= 55:
        n = sum(engine.roll([4, 4]))
        return "one goblin boss and {} goblins".format(n)
    elif die <= 56:
        n = sum(engine.roll([4, 4, 4, 4]))
        return "{} grimlocks".format(n)
    elif die <= 57:
        return "1 ochre jelly"
    elif die <= 58:
        n = sum(engine.roll([10, 10]))
        return "{} giant centipedes".format(n)
    elif die <= 59:
        if dice[1] % 2 == 0:
            return "1 nothic"
        else:
            return "1 giant toad"
    elif die <= 60:
        n = sum(engine.roll([4]))
        m = sum(engine.roll([4, 4, 4, 4, 4]))
        return "{} myconid adults with {} myconid sprouts".format(n, m)
    elif die <= 61:
        if dice[1] % 2 == 0:
            return "1 minotaur skeleton"
        else:
            return "1 minotaur"
    elif die <= 62:
        n = sum(engine.roll([6, 6, 6]))
        return "{} drow".format(n)
    elif die <= 63:
        if dice[1] % 2 == 0:
            return "1 mimic"
        else:
            return "1 doppelganger"
    elif die <= 64:
        n = sum(engine.roll([6])) + 3
        return "{} hobgoblins".format(n)
    elif die <= 65:
        if dice[1] % 2 == 0:
            return "1 intellect devourer"
        else:
            return "1 spectator"
    elif die <= 66:
        n = sum(engine.roll([8])) + 1
        return "{} orcs".format(n)
    elif die <= 68:
        return "a faint tapping coming from inside a nearby wall"
    elif die <= 69:
        if dice[1] % 2 == 0:
            return "1 gibbering mouther"
        else:
            return "1 water weird"
    elif die <= 70:
        n = sum(engine.roll([12]))
        return "{} gas spores".format(n)
    elif die <= 71:
        return "1 giant constrictor snake"
    elif die <= 72:
        n = sum(engine.roll([10]))
        return "{} shadows".format(n)
    elif die <= 73:
        n = sum(engine.roll([3]))
        return "{} grells".format(n)
    elif die <= 74:
        n = sum(engine.roll([4]))
        return "{} wights".format(n)
    elif die <= 75:
        n = sum(engine.roll([8])) + 1
        return "{} quaggoth spore servants".format(n)
    elif die <= 76:
        n = sum(engine.roll([2]))
        return "{} gargoyles".format(n)
    elif die <= 77:
        if dice[1] % 2 == 0:
            n = sum(engine.roll([4]))
            return "{} ogres".format(n)
        else:
            n = sum(engine.roll([3]))
            return "{} ettins".format(n)
    elif die <= 78:
        n = sum(engine.roll([4]))
        return "{} dwarf explorers (veterans)".format(n)
    elif die <= 80:
        n = sum(engine.roll([3]))
        return "an abandoned miners camp splattered with blood and the \
contents of {} dungeoneer's packs".format(n)
    elif die <= 81:
        if dice[1] % 2 == 0:
            return "1 chuul"
        elif dice[1] % 2 == 0:
            return "1 salamander"
    elif die <= 82:
        if dice[1] % 2 == 0:
            n = sum(engine.roll([4]))
            return "{} phase spiders".format(n)
        else:
            n = sum(engine.roll([3]))
            return "{} hook horrors".format(n)
    elif die <= 83:
        n = sum(engine.roll([4, 4, 4, 4, 4]))
        return "{} duergar".format(n)
    elif die <= 84:
        n = sum(engine.roll([3]))
        if n == 1:
            return "1 ghost"
        elif n == 2:
            return "1 flameskull"
        elif n == 3:
            return "1 wraith"
    elif die <= 85:
        return "1 druid with on cave (polar) bear"
    elif die <= 86:
        n = sum(engine.roll([4]))
        m = sum(engine.roll([10, 10]))
        return "1 hobgoblin captain with {} half-ogres and {} hobgoblins".\
            format(n, m)
    elif die <= 87:
        if dice[1] % 2 == 0:
            return "1 earth elemental"
        else:
            return "1 black pudding"
    elif die <= 88:
        n = sum(engine.roll([8]))+1
        return "kuo-toa monitor with {} kuo-toa whips".format(n)
    elif die <= 89:
        n = sum(engine.roll([3]))
        return "1 quaggoth thonot with {} quaggoths".format(n)
    elif die <= 90:
        if dice[1] % 2 == 0:
            return "1 beholder zombie"
        else:
            return "1 bone naga"
    elif die <= 91:
        n = sum(engine.roll([4]))
        m = sum(engine.roll([8, 8]))
        return "1 orc Eye of Gruumsh with {} orogs and {} orcs".format(n, m)
    elif die <= 92:
        n = sum(engine.roll([4]))
        m = sum(engine.roll([10]))
        return "{} ghasts with {} ghouls".format(n, m)
    elif die <= 95:
        return "A reeking puddle where slimy water has dripped \
from the ceiling"
    elif die <= 96:
        if dice[1] % 2 == 0:
            return "1 otyugh"
        else:
            return "1 roper"
    elif die <= 97:
        return "1 vampire spawn"
    elif die <= 98:
        return "1 chimera"
    elif die <= 99:
        return "1 mind flayer"
    elif die <= 100:
        return "1 spirit naga"


def horde(engine):
    ret = "{} copper pieces, {} silver pieces, {} gold pieces, and {} platinum\
 pieces ".format(
           sum(engine.roll([6, 6])) * 100,
           sum(engine.roll([6, 6])) * 1000,
           sum(engine.roll([6, 6, 6, 6, 6, 6])) * 100,
           sum(engine.roll([6, 6, 6])) * 10)
    die = engine.roll([100])[0]
    if die <= 4:
        return ret
    elif die <= 10:
        r = "and {} 25 gp art objects".format(sum(engine.roll([4, 4])))
        return ret + r
    elif die <= 16:
        r = "and {} 50 gp art objects".format(sum(engine.roll([6, 6, 6])))
        return ret + r
    elif die <= 22:
        r = "and {} 100 gp art objects".format(sum(engine.roll([6, 6, 6])))
        return ret + r
    elif die <= 28:
        r = "and {} 250 gp art objects".format(sum(engine.roll([4, 4])))
    elif die <= 32:
        r = "and {} 25 gp art objects".format(sum(engine.roll([4, 4])))
        r2 = magic_items(engine, "a", engine.roll([6])[0])
        return r2 + " and " + ret + r
    elif die <= 36:
        r = "and {} 50 gp art objects".format(sum(engine.roll([6, 6, 6])))
        r2 = magic_items(engine, "a", engine.roll([6])[0])
        return r2 + " and " + ret + r
    elif die <= 40:
        r = "and {} 100 gp art objects".format(sum(engine.roll([6, 6, 6])))
        r2 = magic_items(engine, "a", engine.roll([6])[0])
        return r2 + " and " + ret + r
    elif die <= 44:
        r = "and {} 250 gp art objects".format(sum(engine.roll([4, 4])))
        r2 = magic_items(engine, "a", engine.roll([6])[0])
        return r2 + " and " + ret + r
    elif die <= 49:
        r = "and {} 25 gp art objects".format(sum(engine.roll([4, 4])))
        r2 = magic_items(engine, "b", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 54:
        r = "and {} 50 gp art objects".format(sum(engine.roll([6, 6, 6])))
        r2 = magic_items(engine, "b", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 59:
        r = "and {} 100 gp art objects".format(sum(engine.roll([6, 6, 6])))
        r2 = magic_items(engine, "b", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 63:
        r = "and {} 250 gp art objects".format(sum(engine.roll([4, 4])))
        r2 = magic_items(engine, "b", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 66:
        r = "and {} 25 gp art objects".format(sum(engine.roll([4, 4])))
        r2 = magic_items(engine, "c", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 69:
        r = "and {} 50 gp art objects".format(sum(engine.roll([6, 6, 6])))
        r2 = magic_items(engine, "c", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 72:
        r = "and {} 100 gp art objects".format(sum(engine.roll([6, 6, 6])))
        r2 = magic_items(engine, "c", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 74:
        r = "and {} 250 gp art objects".format(sum(engine.roll([4, 4])))
        r2 = magic_items(engine, "c", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 76:
        r = "and {} 25 gp art objects".format(sum(engine.roll([4, 4])))
        r2 = magic_items(engine, "d", 1)
        return r2 + " and " + ret + r
    elif die <= 78:
        r = "and {} 50 gp art objects".format(sum(engine.roll([6, 6, 6])))
        r2 = magic_items(engine, "d", 1)
        return r2 + " and " + ret + r
    elif die <= 79:
        r = "and {} 100 gp art objects".format(sum(engine.roll([6, 6, 6])))
        r2 = magic_items(engine, "d", 1)
        return r2 + " and " + ret + r
    elif die <= 80:
        r = "and {} 250 gp art objects".format(sum(engine.roll([4, 4])))
        r2 = magic_items(engine, "d", 1)
        return r2 + " and " + ret + r
    elif die <= 84:
        r = "and {} 25 gp art objects".format(sum(engine.roll([4, 4])))
        r2 = magic_items(engine, "f", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 88:
        r = "and {} 50 gp art objects".format(sum(engine.roll([6, 6, 6])))
        r2 = magic_items(engine, "f", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 91:
        r = "and {} 100 gp art objects".format(sum(engine.roll([6, 6, 6])))
        r2 = magic_items(engine, "f", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 94:
        r = "and {} 250 gp art objects".format(sum(engine.roll([4, 4])))
        r2 = magic_items(engine, "f", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 96:
        r = "and {} 100 gp art objects".format(sum(engine.roll([6, 6, 6])))
        r2 = magic_items(engine, "g", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 98:
        r = "and {} 250 gp art objects".format(sum(engine.roll([4, 4])))
        r2 = magic_items(engine, "g", engine.roll([4])[0])
        return r2 + " and " + ret + r
    elif die <= 99:
        r = "and {} 100 gp art objects".format(sum(engine.roll([6, 6, 6])))
        r2 = magic_items(engine, "h", 1)
        return r2 + " and " + ret + r
    elif die <= 100:
        r = "and {} 250 gp art objects".format(sum(engine.roll([4, 4])))
        r2 = magic_items(engine, "h", 1)
        return r2 + " and " + ret + r


def magic_items(engine, table, num):
    objects = []
    for i in range(num):
        if table == "a":
            objects.append(magic_item_a(engine))
        elif table == "b":
            objects.append(magic_item_b(engine))
        elif table == "c":
            objects.append(magic_item_c(engine))
        elif table == "d":
            objects.append(magic_item_d(engine))
        elif table == "e":
            objects.append(magic_item_e(engine))
        elif table == "f":
            objects.append(magic_item_f(engine))
        elif table == "g":
            objects.append(magic_item_g(engine))
        elif table == "h":
            objects.append(magic_item_h(engine))

    if num == 1:
        return objects[0]
    elif num == 2:
        return objects[0] + " and " + objects[1]
    else:
        return ", ".join(objects[0:-1]) + ", and " + objects[-1]


def magic_item_a(engine):
    return "an item from table A"


def magic_item_b(engine):
    return "an item from table B"


def magic_item_c(engine):
    return "an item from table C"


def magic_item_d(engine):
    return "an item from table D"


def magic_item_e(engine):
    return "an item from table E"


def magic_item_f(engine):
    return "an item from table F"


def magic_item_g(engine):
    return "an item from table G"


def magic_item_h(engine):
    return "an item from table H"


def treasure(engine):
    dice = engine.roll([100])
    if dice[0] <= 30:
        return "{} copper and {} electrum pieces".format(
                sum(engine.roll([6, 6, 6, 6])) * 100,
                sum(engine.roll([6])) * 10)
    elif dice[0] <= 60:
        return "{} silver and {} gold pieces".format(
                sum(engine.roll([6, 6, 6, 6, 6, 6])) * 10,
                sum(engine.roll([6, 6])) * 10)
    elif dice[0] <= 70:
        return "{} electrum and {} gold pieces".format(
                sum(engine.roll([6, 6, 6])) * 10,
                sum(engine.roll([6, 6])) * 70)
    elif dice[0] <= 95:
        return "{} gold pieces".format(
                sum(engine.roll([6, 6, 6, 6])) * 10)
    elif dice[0] <= 100:
        return "{} gold and {} platinum pieces".format(
                sum(engine.roll([6, 6])),
                sum(engine.roll([6, 6, 6])))


def general_chamber(die):
    if die <= 1:
        return "antechamber"
    elif die <= 3:
        return "armory"
    elif die <= 4:
        return "audience chamber"
    elif die <= 5:
        return "aviary"
    elif die <= 7:
        return "banquet room"
    elif die <= 10:
        return "barracks"
    elif die <= 11:
        return "latrine"
    elif die <= 12:
        return "bedroom"
    elif die <= 13:
        return "bestiary"
    elif die <= 16:
        return "cell"
    elif die <= 17:
        return "chantry"
    elif die <= 18:
        return "chapel"
    elif die <= 20:
        return "cistern"
    elif die <= 22:
        return "closet"
    elif die <= 24:
        return "conjuring room"
    elif die <= 26:
        return "court"
    elif die <= 29:
        return "crypt"
    elif die <= 31:
        return "dining room"
    elif die <= 33:
        return "divination room"
    elif die <= 34:
        return "dormitory"
    elif die <= 35:
        return "dressing room"
    elif die <= 36:
        return "vestibule"
    elif die <= 38:
        return "gallery"
    elif die <= 40:
        return "game room"
    elif die <= 43:
        return "guard room"
    elif die <= 45:
        return "hall"
    elif die <= 49:
        return "great hall"
    elif die <= 50:
        return "kennel"
    elif die <= 52:
        return "kitchen"
    elif die <= 54:
        return "laboratory"
    elif die <= 57:
        return "library"
    elif die <= 59:
        return "lounge"
    elif die <= 60:
        return "meditatin chamber"
    elif die <= 61:
        return "observatory"
    elif die <= 62:
        return "office"
    elif die <= 64:
        return "pantry"
    elif die <= 66:
        return "prison"
    elif die <= 68:
        return "reception room"
    elif die <= 70:
        return "refactory"
    elif die <= 71:
        return "robing room"
    elif die <= 72:
        return "salon"
    elif die <= 74:
        return "shrine"
    elif die <= 76:
        return "sitting room"
    elif die <= 78:
        return "smithy"
    elif die <= 79:
        return "stable"
    elif die <= 81:
        return "storage room"
    elif die <= 83:
        return "vault"
    elif die <= 85:
        return "study"
    elif die <= 88:
        return "temple"
    elif die <= 90:
        return "throne room"
    elif die <= 91:
        return "torture chamber"
    elif die <= 93:
        return "training room"
    elif die <= 95:
        return "museum"
    elif die <= 96:
        return "nursery"
    elif die <= 98:
        return "well"
    elif die <= 100:
        return "workshop"

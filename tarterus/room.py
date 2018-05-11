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


def num_exit_table(dice, big, extra=True):
    if extra is True:
        die = max(dice)
    else:
        die = dice[0]

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
        num = num_exit_table(dice, big, engine.extra_branch)

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
        num = num_exit_table(dice, big, engine.extra_branch)
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
    ret = "<p><b>A {} foot by {} foot {}.</b></p>".\
          format(d['w'], d['h'], chamber_type)
    contents = chamber_contents(engine, dice[1])
    ret += contents
    return ret

# Build new chart for types of monsters (primary inhabitant etc.)?
def chamber_contents(engine, die=0):
    die = engine.roll([100])[0]
    a, b = "", ""
    try:
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
            return "<p>monsters: {}.</p>".format(chamber_monster(engine))
        elif die <= 50:
            return "<p>monsters: {} with {}.</p>".format(
                    chamber_monster(engine), which_treasure(engine))
        elif die <= 58:
            return "<p>" + chamber_hazard(engine) + " and " + treasure(engine) + "</p>"
        elif die <= 63:
            return "<p>" + chamber_obstacle(engine) + "</p>"
        elif die <= 73:
            return "<p>" + chamber_trap(engine) + "</p>"
        elif die <= 76:
            a = chamber_trap(engine)
            if a is None:
                raise RuntimeError("None trap!")
            b = which_treasure(engine)
            return "<p>" + a + " protecting " +\
                    b + "</p>"
        elif die <= 80:
            return "<p>" + chamber_trick(engine) + "</p>"
        elif die <= 88:
            return "<p> This is an otherwise empty room </p>"
        elif die <= 94:
            return "<p>" + chamber_hazard(engine) + "</p>"
        elif die <= 100:
            return "<p>" + which_treasure(engine) + "</p>"
    except Exception as e:
        raise RuntimeError("describe chamber ({}, {}) with die roll {} raised {}".format(a, b, die, e))


def chamber_trick(engine):
    try:
        die1, die2 = engine.roll([20,100])
        ret = "There is a trick. "
        if die1 <= 1:
            ret += "A book"
        elif die1 <= 2:
            ret += "A preserved brain in a jar"
        elif die1 <= 3:
            ret += "A burning fire"
        elif die1 <= 4:
            ret += "A cracked gem"
        elif die1 <= 5:
            ret += "A door"
        elif die1 <= 6:
            ret += "A fresco"
        elif die1 <= 7:
            ret += "A piece of furniture"
        elif die1 <= 8:
            ret += "A glass sculpture"
        elif die1 <= 9:
            ret += "A mushroom field"
        elif die1 <= 10:
            ret += "A painting"
        elif die1 <= 11:
            ret += "A plant or tree"
        elif die1 <= 12:
            ret += "A pool of water"
        elif die1 <= 13:
            ret += "Runes engraved on the wall"
        elif die1 <= 14:
            ret += "A skull"
        elif die1 <= 15:
            ret += "A sphere of magical energy"
        elif die1 <= 16:
            ret += "A statue"
        elif die1 <= 17:
            ret += "A stone obelisk"
        elif die1 <= 18:
            ret += "A suit of armor"
        elif die1 <= 19:
            if engine.roll([2])[0] <= 1:
                ret += "A tapestry"
            else:
                ret += "A rug"
        elif die1 <= 20:
            ret += "A target dummy"
        else:
            ret += "A bad die roll"

        if die2 <= 3:
            return ret + " ages the first person to touch it."
        elif die2 <= 6:
            return ret + " when touched animates, or animates a nearby object."
        elif die2 <= 10:
            return ret + " asks three skill testing questions. If answered,\
a reward appears."  # TODO: what kind of reward?
        elif die2 <= 13:
            return ret + " bestows a resistance or vulnerability."
        elif die2 <= 16:
            return ret + " changes a character's alignment, personality, size,\
or appearance when touched."
        elif die2 <= 19:
            return ret + " transmutes one substance into another, such as\
gold to lead or metal to brittle crystal."
        elif die2 <= 22:
            return ret + " creates a force field."
        elif die2 <= 26:
            return ret + " creates an illusion."
        elif die2 <= 29:
            die3, die4 = engine.roll([4, 4])
            return ret + " suppresses magic items for {} hours.".format(
die3 + die4)
        elif die2 <= 32:
            if engine.roll([2])[0] <= 1:
                return ret + " enlarges characters."
            else:
                return ret + " reduces characters."
        elif die2 <= 35:
            return ret + " a 'Magic Mouth' speaks a riddle."
        elif die2 <= 38:
            return ret + " 'Confusion (save DC 15) targets all characters in 10 ft."
        elif die2 <= 41:
            if engine.roll([2])[0] <= 1:
                return ret + " gives true directions."
            else:
                return ret + " gives false directions."
        elif die2 <= 44:
            return ret + " grants a 'Wish' (holy shit)."
        elif die2 <= 47:
            return ret + " flies around to avoid being touched."
        elif die2 <= 50:
            return ret + " casts 'Gaeas' on the characters."
        elif die2 <= 53:  # TODO: does more
            return ret + " reverses gravity."
        elif die2 <= 56:
            return ret + " induces greed."
        elif die2 <= 59:
            return ret + " contains an imprisoned creature."
        elif die2 <= 62:
            return ret + " locks the exits. (DC 17)"
        elif die2 <= 65:
            return ret + " offers a game of chance for a reward of piece of\
 information."
        elif die2 <= 68:
            return ret + " helps or harms certain types of creatures."
        elif die2 <= 71:
            return ret + " casts polymorph on the characters (lasts 1 hour)"
        elif die2 <= 75:
            return ret + " presents a puzzle or a riddle"
        elif die2 <= 78:
            return ret + " prevents movement"
        elif die2 <= 81: # TODO: does more
            return ret + " releases coins & gems"
        elif die2 <= 84:
            return ret + " turns into or summons a monster"
        elif die2 <= 87:
            return ret + " casts 'Suggestion' on the characters."
        elif die2 <= 90:
            return ret + " wails loudly when touched."
        elif die2 <= 93:
            return ret + " talks"
        elif die2 <= 97:
            return ret + " teleports the characters to another place."
        elif die2 <= 100:
            return ret + " swaps two of the characters' minds."
        else:
            return " dice problem."
    except Exception as e:
        raise RuntimeError("chamber_trick with dice {} {} threw {}.".format(die1, die2, e))

def which_treasure(engine):
    dice = engine.roll([20])
    try:
        if dice[0] <= 17:
            return treasure(engine)
        elif dice[0] <= 20:
            return horde(engine)
    except Exception as e:
        raise RuntimeError("which_treasure with dice {} threw {}".format(dice, e))


def chamber_obstacle(engine):
    die = engine.roll([20])[0]
    ret = "There is an obstacle: "
    try:
        if die <= 1:
            die2 = engine.roll([10])[0]
            ret += "There is an antilife aura with radius {} ft. While in the\
aura, creatures cannot gain hit points.".format(die2 * 10)
        elif die <= 2:
            ret += "There are strong winds that reduce speed by half and\
impose disadvantage on ranged attacks."
        elif die <= 3:
            ret += "A 'Blade Barrier' spell blocks a passage."
        elif die <= 8:
            if engine.roll([2])[0] <= 1:
                ret += "There has been a cave-in here. The room is difficult\
terrain."
            else:
                ret += "The ceiling caves in when the players enter the room\
make a DC 15 Dex save or take 2d10 damage, half as much with a successful\
save."
        elif die <= 12:  # TODO: Implement chasms
            ndice = engine.roll([4, 6, 6])
            width = ndice[0] * 10
            depth = ndice[1] * 10 + ndice[2] * 10
            ret += "There is a chasm {} feet wide and {} feet deep.".format(
width, depth)
        elif die <= 14:  # TODO: Implement water
            ndice = engine.roll([10, 10])
            depth = ndice[0] + ndice[1]
            ret += "The floor is sunken in and below {} feet of water.".format(
depth)
        elif die <= 15:  # TODO: Implement lava flows
            ret += "Lava flows through this area!"
            if engine.roll([2])[0] >= 1:
                ret += " There is a stone bridge over it."
        elif die <= 16:
            ret += "Giant mushrooms must be hacked at to pass through this\
area."
        elif die <= 17:
            ret += "Poisonous gas deals 1d6 damage per minute of exposure."
        elif die <= 18:
            ret += "There is a 'Reverse Gravity' spell in effect."
        elif die <= 19:
            ret += "A 'Wall of Fire' blocks the area."
        elif die <= 20:
            ret += "A 'Wall of Force' blocks the area."
        else:
            ret += "the dice messed up."
        return ret
    except Exception as e:
        return "a chamber hazard error on die roll {} with error {}".format(
            die, e)


def chamber_hazard(engine):
    die = engine.roll([20])[0]
    ret = "There is a hazard. "
    try:
        if die <= 3:
            return ret + "There is a Brown Mold."
        elif die <= 8:
            return ret + "There is a Green Slime."
        elif die <= 10:
            return ret + "There is a Shrieker."
        elif die <= 15:
            return ret + "There are spiderwebs. DC 15 to see. A creature that steps\
in to them becomes restrained and must make a DC 20 escape check."
        elif die <= 17:
            return ret + "There is a violet fungus."
        elif die <= 20:
            return ret + "There is a yellow mold."
        else:
            return ret + "Die roll problem."
    except Exception as e:
        return "a hazard error with die roll {} with error {}".format(die, e)


def chamber_trap(engine):
    ret = ""
    dice = engine.roll([6, 6, 100])

    try:
       if dice[1] <= 2:
           damage = "1d10"
           dc = 9 + engine.roll([2])[0]
           bonus = 2 + engine.roll([3])[0]
       elif dice[1] <= 5:
           damage = "2d10"
           dc = 11 + engine.roll([4])[0]
           bonus = 15 + engine.roll([5])[0]
       elif dice[1] <= 6:
           damage = "3d10"
           dc = 15 + engine.roll([5])[0]
           bonus = 8 + engine.roll([4])[0]
   
       ret += "There is a trap, the DC to spot & disarm it is {}. ".format(dc)
   
       if dice[0] <= 1:
           ret += "An area of the floor is trapped: "
       elif dice[0] <= 2:
           ret += "A door or hallway has a trap triggered by moving through it: "
       elif dice[0] <= 3:
           ret += "A doorknob or statue is has a trap triggered by\
    touching it: "
       elif dice[0] <= 4:
           die2 = engine.roll([2])[0]
           if die2 <= 1:
               ret += "There is a trapped treaure chest: "
           elif die2 <= 2:
               ret += "There is a trapped door triggered by opening it (if no\
    no door, there is a trapped treasure chest): "
       elif dice[0] <= 5:
           die2 = engine.roll([2])[0]
           if die2 <= 1:
               ret += "There is a mural, looking at it triggers a trap: "
           elif die2 <= 2:
               ret += "There is an arcane symbol, looking at it triggers a trap: "
       elif dice[0] <= 6:
           ret += "An object in the room that triggers a trap when it is moved: "
       
       if dice[2] <= 4:
           ret += "Magic missiles fire out, doing {} damage.".format(damage)
       elif dice[2] <= 7:
           ret += "A collapsing floor deposits the characters into a\
   pit. DC {} Dex save to avoid {} damage.".format(dc, damage)
       elif dice[2] <= 10:
           die2 = engine.roll([2])[0]
           if die2 <= 1:
               ret += "A ceiling block falls,\
   DC {} Dex save to avoid {} damage".format(dc, damage)
           elif die2 <= 2:
               ret += "The entire ceiling collapses, dealing {} damage.\
   ".format(damage)
       elif dice[2] <= 12:
           ret += "The doors lock, the passages close and the ceiling lowers,\
    doing {} damage if the players cannot escape. DC to pick locks or break doors\
    is {}".format(damage, dc)
       elif dice[2] <= 14:
           ret += "A chute opens in the floor, DC {} Dex save to avoid going down\
    to a lower level.".format(dc)
       elif dice[2] <= 16:
           ret += "A clanging noise alerts monsters in all rooms connected to\
   this room or at the end of halls connected to this room."
       elif dice[2] <= 19:
           ret += "A disintegrate spell is triggered. Spell save DC is {} and the\
    spell does {} damage.".format(dc, damage)
       elif dice[2] <= 23:
           ret += "There is a contact poison or acid. Make a DC {} Con save or\
    take {} damage.".format(dc, damage)
       elif dice[2] <= 27:
           ret += "Fire shoots out. Take {} damage or half that much with a DC {}\
    Dex save.".format(damage, dc)
       elif dice[2] <= 30:
           ret += "The spell 'Flesh to Stone' is triggered. The spell save DC is\
    {}.".format(dc)
       elif dice[2] <= 33:
           die2 = engine.roll([2])[0]
           if die2 <= 1:
               ret += "The floor collapses. Make a DC {} Dex save or fall in and\
    take {} damage."
           elif die2 <= 2:
               ret += "The floor is (or becomes) an illusion. Make a DC {} Int\
    save or you fail to see it and fall, taking {} damage.".format(dc, damage)
       elif dice[2] <= 36:
           die2 = engine.roll([6])[0]
           if die2 <= 1:
               ret += "A vent releases blinding gas. Everyone in the room make a\
    DC {} Con save or become blinded. Reroll the save at the end of each round.\
   ".format(dc)
           elif die2 <= 2:
               ret += "A vent releases acidic gas. Everyone in the room make a DC\
    {} Con save or take {} damage.".format(dc, damage)
           elif die2 <= 3:
               ret += "A vent releases obscuring gas. Everything in the room\
    is heavily obscured. Creatures without blindsense or similar make attack\
    rolls with disadvantage."
           elif die2 <= 4:
               ret += "A vent releases paralyzing gas. Everyone in the room\
    make a DC {} Con save or become paralyzed. Reroll the save at the end of each\
    round.".format(dc)
           elif die2 <= 5:
               ret += "A vent releases poisonous gas. Everyone in the room\
    make a DC {} Con save or take {} damage and gain the poisoned condition until\
    your next long rest.".format(dc, damage)
           elif die2 <= 6:
               ret += "A vent release sleep gas. Everyone in the room make a DC\
    {} Con save or fall asleep until shaken awake.".format(dc)
       elif dice[2] <= 39:
           ret += "The floor is electrified. Take {} damage or half as much\
    with a DC {} Dex save.".format(damage, dc)
       elif dice[2] <= 43:
           ret += "There is a 'Glyph of Warding' spell on the triggering object\
    the spell save DC is {}.".format(dc)
       elif dice[2] <= 46:
           ret += "A huge wheeled statue rolls down a corridor, everyone in its\
    path make a DC {} Dex save or take {} damage and be knocked prone.\
   ".format(dc, damage)
       elif dice[2] <= 49:
           ret += "A lightning bolt shoots from the wall. Take {} damage or half\
    that with a DC {} Dex save.".format(damage, dc)
       elif dice[2] <= 52:
           die2 = engine.roll([2])[0]
           if die2 <= 1:
               ret += "The doors lock, the passages close, and the room fills with water.\
    DC to pick locks or break a doors is {}. After the first try to pick a lock\
    or lift a door, the doors are underwater and creatures without a swim speed\
    make checks at disadvantage.".format(dc)
           if die2 <= 2:
               ret += "The doors lock, the passages close, and the room fills\
    with acid. The acid does {} damage per round. The DC to pick locks or break\
    doors is {}. After the first try to pick a lock or break a door, the doors\
    are submerged and creatures without a swim speed make checks with\
    disadvantage.".format(damage, dc)
       elif dice[2] <= 56:
               ret += "The trap attacks with darts. The attack bonus is {} and\
    the darts do {} damage.".format(bonus, damage)
       elif dice[2] <= 59:
           die2 = engine.roll([3])[0]
           if die2 <= 1:
               ret += "A weapon in the room becomes an Animated Object."
           elif die2 <= 2:
               ret += "A suit of armor in the room becomes an Animated\
   Object."
           elif die2 <= 3:
               ret += "A rug in the room becomes an Animated Object."
       elif dice[2] <= 62:
           ret += "A blade swings across the room or hall, dealing {} damage to\
    anyone in its path failing a DC {} Dex save.".format(damage, dc)
       elif dice[2] <= 67:
           die2 = engine.roll([8])[0]
           ret += "A hidden pit opens. Make a DC {} save to avoid falling in and\
    taking {} damage.".format(dc, damage)
           if die2 <= 6:
               pass
           elif die2 <= 7:
               ret += " there is a Black Pudding at the bottom of the pit."
           elif die2 <= 8:
               ret += " there is a Gelatinous Cube at the bottom of the pit."
       elif dice[2] <= 70:
           ret += "A hidden pit opens. Make a DC {} save or fall in taking half\
    of {} damage. After each failed attempt to climb out or otherwise escape\
    (DC is also {}) take {} damage.".format(dc, damage, dc, damage)
       elif dice[2] <= 73:
           ret += "A shallow pit opens up. Make a DC {} save to avoid falling in\
    the pit closes and locks and fills with water. The DC to pick the lock is {}.\
   ".format(dc, dc)
       elif dice[2] <= 77:
           ret += "A scithing blade attacks with a bonus of {} doing {} damage.\
   ".format(bonus, damage)
       elif dice[2] <= 81:
           die2 = engine.roll([2])[0]
           if die2 <= 1:
               ret += "A spear attacks with a bonus of {} doing 1d8 damage.\
".format(bonus)
           elif die2 <= 2:
               ret += "A spear attacks with a bonus of {} doing 1d8 damage. If\
    you are hit, make a DC {} Con save or become poisoned and take {} damage.\
   ".format(bonus, dc, damage)
       elif dice[2] <= 84:
           ret += "The floor collapses onto spikes. Make a DC {} Dex save to\
    avoid {} damage.".format(dc, damage)
       elif dice[2] <= 88:
           die2 = engine.roll([2])[0]
           if die2 <= 1:
               ret += "A Thunderwave spell (DC {}) pushes players into spiked walls\
    doing {} damage.".format(dc, damage)
           elif die2 <= 2:
               ret += "A Thunderwave spell (DC {}) pushes players into a pit for\
    {} damage.".format(dc, damage)
       elif dice[2] <= 91:
           die2 = engine.roll([2])[0]
           if die2 <= 1:
               ret += "Steel "
           elif die2 <= 2:
               ret += "Stone "
           ret += "jaws restrain a a character. The Strength check to get out has\
    a DC of {}.".format(dc)
       elif dice[2] <= 94:
           ret += "A stone block smashes across the room or hallway. Make a DC\
   {} Dex save or take {} damage.".format(dc, damage)
       elif dice[2] <= 97:
           ret += "There is a Symbol spell. Spell save DC is {}.".format(dc)
       elif dice[2] <= 100:
           ret += "The doors lock and the passages close and the walls slide\
    together crushing the characters. The walls do {} damage to the players and\
    the DC of any ability check related to the trap is {}.".format(damage, dc)
    except Exception as e:
        raise RuntimeError("trap error with dice {} raising {}".format(dice, e))
    
    if ret is None:
        return "NONE TRAP DIE={}".format(dice[2])
    return ret


def chamber_monster(engine):
    dice = engine.roll([100, 20])
    die = dice[0]

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
    else: 
        return "MONSTER TABLE ERROR"


def horde(engine):
    ret = "{} copper pieces, {} silver pieces, {} gold pieces, and {} platinum\
 pieces ".format(
           sum(engine.roll([6, 6])) * 100,
           sum(engine.roll([6, 6])) * 1000,
           sum(engine.roll([6, 6, 6, 6, 6, 6])) * 100,
           sum(engine.roll([6, 6, 6])) * 10)
    die = engine.roll([65])[0]
    try:
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
        else:
            return "HORDE ERROR"
    except Exception as e:
        raise RuntimeError("horde with dice {} raised {}".format(die, e))

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
        else:
            return "MAGIC ITEMS TABLE ERROR"

    if num == 1:
        return objects[0]
    elif num == 2:
        return objects[0] + " and " + objects[1]
    else:
        return ", ".join(objects[0:-1]) + ", and " + objects[-1]


def magic_item_a(engine):
    die = engine.roll([100])[0]
    if die <= 50:
        return "a Potion of Healing"
    elif die <= 60:
        return "a Cantrip Spell Scroll"  # Expand This
    elif die <= 70:
        return "a Potion of Climbing"
    elif die <= 90:
        return "a Spell Scroll (1st level)"  # Expand This
    elif die <= 94:
        return "a Spell Scroll (2nd level)"  # Expand This
    elif die <= 98:
        return "Potion of Greater Healing"
    elif die <= 99:
        return "Bag of Holding"
    elif die <= 100:
        return "Driftglobe"


def magic_item_b(engine):
    die = engine.roll([100])[0]
    if die <= 15:
        return "a Potion of Greater Healing"
    elif die <= 22:
        return "a Potion of Fire Breath"
    elif die <= 29:
        return "a Potion of Resistance"
    elif die <= 34:
        die2 = engine.roll([6])[0]
        if die2 <= 2:
            return "a +1 Arrow"
        elif die2 <= 4:
            return "a +1 Crossbow Bolt"
        elif die2 <= 6:
            return "a +1 Sling Stone"
    elif die <= 39:
        return "a Potion of Animal Friendship"
    elif die <= 44:
        return "a Potion of Hill Giant Strength"
    elif die <= 49:
        return "a Potion of Growth"
    elif die <= 54:
        return "a Potion of Water Breathing"
    elif die <= 59:  # expand
        return "a 2nd level Spell Scroll"
    elif die <= 64:  # expand
        return "a 3rd level Spell Scroll"
    elif die <= 67:
        return "a Bag of Holding"
    elif die <= 70:
        return "a Container of Keoghtom's Ointment"
    elif die <= 73:
        return "a Container of Oil of Slipperiness"
    elif die <= 75:
        return "a Bag of Dust of Disappearance"
    elif die <= 77:
        return "a Bag of Dust of Dryness"
    elif die <= 79:
        return "a Bag of Dust of Sneezing and Choking"
    elif die <= 81:
        die2 = engine.roll([4])[0]
        if die2 <= 1:
            return "a Blue Sapphire Elemental Gem"
        elif die2 <= 2:
            return "a Yellow Diamond Elemental Gem"
        elif die2 <= 3:
            return "a Red Corundum Elemental Gem"
        elif die2 <= 4:
            return "an Emerald Elemental Gem"
    elif die <= 83:
        return "a Philter of Love"
    elif die <= 84:
        return "an Alchemy Jug"
    elif die <= 85:
        return "a Cap of Water Breathing"
    elif die <= 86:
        return "a Cloak of the Manta Ray"
    elif die <= 87:
        return "a Driftglobe"
    elif die <= 88:
        return "a Pair of Goggles of the Night"
    elif die <= 89:
        return "a Helm of Comprehending Languages"
    elif die <= 90:
        return "an Immovable Rod"
    elif die <= 91:
        return "a Lantern of Revealing"
    elif die <= 92:  # expand
        return "Mariner's Armor"
    elif die <= 93:  # expand
        return "Mithral Armor"
    elif die <= 94:
        return "A Potion of Poison"
    elif die <= 95:
        return "A Ring of Swimming"
    elif die <= 96:
        return "A Robe of Useful Items"
    elif die <= 97:
        return "A Rope of Climbing"
    elif die <= 98:
        return "A Saddle of the Cavalier"
    elif die <= 99:
        return "A Wand of Magic Detection"
    elif die <= 100:
        return "A Wand of Secrets"
    else:
        return "AN ERROR IN MAGIC ITEM TABLE B"


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
    else:
        return "AN ERROR IN TREASURE TABLE"


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

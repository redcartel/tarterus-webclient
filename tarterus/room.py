from tarterus.maparray import MapArray
from tarterus.graphpaper import back, turn_positive  # , vector, right, left,
from tarterus.graphpaper import advance  # turn_across, empty, middle_value
from tarterus.graphpaper import is_positive, gt_or_eq
# from random import randint

DICE_ARRAY = [15, 10, 10]

DONT_OVERLAP_SQUARES = ['room', 'hall', 'stup', 'sdwn']


def no_overlap(squares, checked=None):
    global DONT_OVERLAP_SQUARES
    if checked is None:
        checked = DONT_OVERLAP_SQUARES

    def not_overlap(msquare):
        if msquare[0] not in checked:
            return True

    return all(not_overlap(s) for s in squares)


def rect_fits(maparray, x, y, w, h, checked=None):
    if x <= 0 or y <= 0:
        return False
    if x + w >= maparray.w or y + h >= maparray.h:
        return False
    return no_overlap(maparray[x:x+w, y:y+w].squares(), checked)


def room(w, h, rsquare):
    rnum = rsquare[1]
    room = MapArray(rsquare, (w, h))
    room[0:w:w-1, 1:h-1] = ('vwal', rnum)
    room[1:w-1, 0:h:h-1] = ('hwal', rnum)
    room[0:w:w-1, 0] = ('tcor', rnum)
    room[0:w:w-1, h-1] = ('bcor', rnum)
    return room


def draw_room(maparray, x, y, w, h, rsquare):
    if rect_fits(maparray, x, y, w, h):
        maparray[x:x+w, y:y+h] = room(w, h, rsquare)
        return True
    else:
        return False


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

def find_loc(maparray, x, y, w, h, direction, width, dice):
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
        elif not rect_fits(maparray, x0, y0, w, h):
            pass
        else:
            return x0, y0
    return False, False


def place_entrance(maparray, origin, x, y, direction, width, psquare, dice):
    if origin == "door":
        maparray[x, y] = ('door', psquare[1])
    elif origin == "passage":
        if direction in ["e", "w"]:
            maparray[x, y: y+width] = ('open', psquare[1])
        elif direction in ["n", "s"]:
            maparray[x: x+width, y] = ('open', psquare[1])


# Tables. Currently does not handle over-wide passage entrances well
# TODO: wide passages
# 20 x 20 room
def room_table_1_2(engine, origin, x, y, direction, width, rsquare, dice):
    x0, y0 = find_loc(engine.maparray, x, y, 6, 6, direction, width, dice)
    if x0 is not False:
        draw_room(engine.maparray, x0, y0, 6, 6, rsquare)
        place_entrance(engine.maparray, origin, x, y,
                       direction, width, rsquare, dice)


# 30 x 30 room
def room_table_3_4(engine, origin, x, y, direction, width, rsquare, dice):
    x0, y0 = find_loc(engine.maparray, x, y, 8, 8, direction, width, dice)
    if x0 is not False:
        draw_room(engine.maparray, x0, y0, 8, 8, rsquare)
        place_entrance(engine.maparray, origin, x, y,
                       direction, width, rsquare, dice)
    else:
        print("step_down")
        room_table_1_2(engine, origin, x, y, direction, width, rsquare, dice)


# 40 x 40 room
def room_table_5_6(engine, origin, x, y, direction, width, rsquare, dice):
    x0, y0 = find_loc(engine.maparray, x, y, 10, 10, direction, width, dice)
    if x0 is not False:
        draw_room(engine.maparray, x0, y0, 10, 10, rsquare)
        place_entrance(engine.maparray, origin, x, y,
                       direction, width, rsquare, dice)
    else:
        room_table_3_4(engine, origin, x, y, direction, width, rsquare, dice)


# 20 x 30 room
def room_table_7_9(engine, origin, x, y, direction, width, rsquare, dice):
    a, b = 6, 8
    if dice[0] % 2 == 0:
        a, b = b, a

    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        draw_room(engine.maparray, x0, y0, a, b, rsquare)
        place_entrance(engine.maparray, origin, x, y,
                       direction, width, rsquare, dice)
        return True

    a, b = b, a
    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        draw_room(engine.maparray, x0, y0, a, b, rsquare)
        place_entrance(engine.maparray, origin, x, y,
                       direction, width, rsquare, dice)
        return True

    return room_table_1_2(engine, origin, x, y, direction,
                          width, rsquare, dice)


# 30 x 40 room
def room_table_10_12(engine, origin, x, y, direction, width, rsquare, dice):
    a, b = 8, 10
    if dice[0] % 2 == 0:
        a, b = b, a

    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        draw_room(engine.maparray, x0, y0, a, b, rsquare)
        place_entrance(engine.maparray, origin, x, y,
                       direction, width, rsquare, dice)
        return True

    a, b = b, a
    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        a, b = b, a
        x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
        draw_room(engine.maparray, x0, y0, a, b, rsquare)
        place_entrance(engine.maparray, origin, x, y,
                       direction, width, rsquare, dice)
        return True

    return room_table_7_9(engine, origin, x, y, direction,
                          width, rsquare, dice)


# 40 x 50 room
def room_table_13_14(engine, origin, x, y, direction, width, rsquare, dice):
    a, b = 10, 12
    if dice[0] % 2 == 0:
        a, b = b, a

    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        draw_room(engine.maparray, x0, y0, a, b, rsquare)
        place_entrance(engine.maparray, origin, x, y,
                       direction, width, rsquare, dice)
        return True

    a, b = b, a
    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        draw_room(engine.maparray, x0, y0, a, b, rsquare)
        place_entrance(engine.maparray, origin, x, y,
                       direction, width, rsquare, dice)
        return True

    return room_table_10_12(engine, origin, x, y, direction,
                            width, rsquare, dice)


# 50 x 80 room
def room_table_15(engine, origin, x, y, direction, width, rsquare, dice):
    a, b = 12, 18
    if dice[0] % 2 == 0:
        a, b = b, a

    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        draw_room(engine.maparray, x0, y0, a, b, rsquare)
        place_entrance(engine.maparray, origin, x, y,
                       direction, width, rsquare, dice)
        return True

    a, b = b, a
    x0, y0 = find_loc(engine.maparray, x, y, a, b, direction, width, dice)
    if x0 is not False:
        draw_room(engine.maparray, x0, y0, a, b, rsquare)
        place_entrance(engine.maparray, origin, x, y,
                       direction, width, rsquare, dice)
        return True

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
        draw_room(engine.maparray, x, y, *width, rsquare)
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
            room_table_3_4(engine, origin, x, y, direction,
                           width, rsquare, dice)
        elif width <= 8:
            room_table_5_6(engine, origin, x, y, direction,
                           width, rsquare, dice)
    elif die_roll <= 6:
        # 40x40
        room_table_5_6(engine, origin, x, y, direction, width, rsquare, dice)
    elif die_roll <= 9:
        # 20x30
        if width <= 6:
            room_table_7_9(engine, origin, x, y, direction,
                           width, rsquare, dice)
        elif width <= 8:
            room_table_10_12(engine, origin, x, y, direction,
                             width, rsquare, dice)
    elif die_roll <= 12:
        # 30x40
        room_table_10_12(engine, origin, x, y, direction, width, rsquare, dice)
    elif die_roll <= 14:
        # 40x50
        room_table_13_14(engine, origin, x, y, direction, width, rsquare, dice)
    elif die_roll <= 15:
        # 50x80
        room_table_15(engine, origin, x, y, direction, width, rsquare, dice)

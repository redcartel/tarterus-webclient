from tarterus.maparray import MapArray
from tarterus.graphpaper import back, turn_positive  # , vector, right, left,
from tarterus.graphpaper import advance  # turn_across, empty, middle_value
from tarterus.graphpaper import is_positive, gt_or_eq
# from random import randint

DICE_ARRAY = [20]

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


# attempt to place the room at an offset, derived
# from 2 dice, from the door location, then
# move it along the axis orthogonal to the direction of the door until a
# placement that does not overlap illegal tiles is found
# random offset assumed to be determined by 2d10
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
        # if not is_positive(direction):
        #    x0, y0 = advance(x0, y0, direction, d_length - 1)
# advance offset
        base_offset = base_offset + 1
        offset = base_offset % (o_length - 2)
# check if wider entrance fits orthogonal wall
# dummy values pass check
        # x1, y1, x2, y2 = (2, 2, 0, 0)
        # if width > 1:
            # x1, y1 = advance(x0, y0, o_direction, o_length - 1)
            # x2, y2 = advance(x, y, o_direction, o_length - 1)
        # if gt_or_eq((x2, y2), (x1, x1), o_direction):
            # pass
        # elif rect_fits(maparray, x0, y0, w, h):
        if rect_fits(maparray, x0, y0, w, h):
            return x0, d_length
    return False, False


def place_entrance(maparray, origin, x, y, direction, width, psquare, dice):
    maparray[x, y] = ('door', psquare[1])


# 40 x 40 room
def room_table_1(engine, origin, x, y, direction, width, rsquare, dice):
    x, y = find_loc(engine.maparray, origin, x, y, 10, 10,
                    direction, width, dice)
    draw_room(engine.maparray, x, y, 10, 10, rsquare)
    place_entrance(engine.maparray, origin, x, y,
                   direction, width, rsquare, dice)


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
    elif die_roll <= 20:
        room_table_1(engine, origin, x, y, direction, width, rsquare, dice)

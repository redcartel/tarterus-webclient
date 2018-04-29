# from tarterus.maparray import MapArray
from tarterus.graphpaper import right, left, back, turn_positive
from tarterus.graphpaper import is_positive, turn_across
from tarterus.graphpaper import advance, middle_value  # , empty
# from random import randint

DICE_ARRAY = [19, 12, 20]


# given a square, width, and direction, find an empty orthogonal row of squares
# of the given width that includes the square
def find_pass_loc(engine, x, y, w, direction, dice, checked=None):
    x0, y0 = x, y
    if w == 1:
        if engine.maparray[x0, y0][0] == 'void':
            return x, y
        else:
            return False, False

    offset = (dice[0] + dice[1] - 17) % w
    if (dice[0] % 2 == 0):
        delta = 1
    else:
        delta = -1

    for search_pos in range(w):
        d = (offset + delta * search_pos) % w
        x1, y1 = advance(x0, y0, back(turn_positive(direction)), d)
        success = True
        for i in range(w):
            x2, y2 = advance(x1, y1, turn_positive(direction), i)
            if engine.maparray[x2, y2][0] != 'void':
                success = False
                break
        if success is True:
            return x1, y1
    return False, False


# given a door origin, place a passage of a given width
def place_door_pass(engine, x, y, direction, w, dice):
    w0 = w
    x0, y0 = advance(x, y, direction, 1)
    while w0 > 0:
        x1, y1 = find_pass_loc(engine, x0, y0, w0, direction, dice)
        if x1 is not False:
            return x1, y1, w0
        else:
            if w0 > 2:
                w0 = w0 - 2
            else:
                w0 = w0 - 1
    return False, False, False


def draw_passage_section(engine, x, y, direction, width, length, psquare):
    o_dir = turn_positive(direction)
    origins = [advance(x, y, o_dir, i) for i in range(width)]
    step_out = False
    blocks = []
    for i in range(length):
        new_origins = origins[:]
        for x0, y0 in origins:
            x1, y1 = advance(x0, y0, direction, i)
            if x1 <= 0 or x1 + 1 >= engine.maparray.w:
                new_origins.remove((x0, y0))
                blocks.append((x1, y1))
            elif y1 <= 0 or y1 + 1 >= engine.maparray.h:
                new_origins.remove((x0, y0))
                blocks.append((x1, y1))
            elif engine.maparray[x1, y1][0] != 'void':
                engine.log(":: draw_passage_section block")
                engine.log("\tblock at {}, remove {}".
                           format((x1, y1), (x0, y0)))
                new_origins.remove((x0, y0))
                blocks.append((x1, y1))
            else:
                engine.maparray[x1, y1] = psquare
        origins = new_origins
        if step_out is True:
            break
        if len(origins) < width:
            step_out = True
    if step_out is False:
        x2, y2 = advance(x, y, direction, length)
        return (True, {"next_square": (x2, y2)})
    else:
        return (False, {"blocks": blocks})

# NOTE: Drawing passages only if the way is completely clear might be a toggle
#   option to generate sparser maps. For a later version
# draw a passage if it is an entirely clear path
# TODO (if needed): return more meaningful blocks data
# def passage_no_block(maparray, x, y, direction, width, length, psquare):
#     c = coords(x, y, direction, width, length)
#     if empty(maparray, c['x1'], c['y1'], c['w'], c['h']):
#         maparray[c['x1']:c['x2'], c['y1']:c['y2']] = psquare
#         return {"result": "success",
#                 "next_saure": (c['nx'], c['ny'])
#                 }
#     else:
#         return {"result": "blocked", "blocks": []}


# TODO columns. I guess that's why this is returning a damn dictionary.
# dieroll = -1 : d12 (passage from passage)
# dieroll = 20 : d20 (passage from chamber)
# TODO: move passage width determination to this module and don't rely on
# element creation to determine width
def passage_width_table(die_roll=-1, from_chamber=False):
    if die_roll == -1:
        raise Exception

    if die_roll <= 2:
        return {"width": 1}
    elif die_roll <= 12:
        return {"width": 2}
    elif die_roll <= 14:
        return {"width": 4}
    elif die_roll <= 16:
        return {"width": 6}
    else:
        return {"width": 8}


# Table from pg. 290
# Current behavior is to only add branches if the main corridor of the passage
# draws without being blocked.
# straight 30ft, no doors or side passages & continue
def passage_table_1_2(engine, origin, x, y, direction, width, psquare, dice):
    catch = draw_passage_section(engine, x, y, direction, width, 6, psquare)
    if catch[0] is True:
        nx, ny = catch[1]['next_square']
        engine.add(['hall', 'passage', nx, ny, direction, width, psquare])
        return (True, (x, y, width, []))
    else:
        return (True, (x, y, width, catch[1]['blocks']))


# straight 20 ft, door to the right, 10 more feet & continue
def passage_table_3(engine, origin, x, y, direction, width, psquare, dice):
    catch1 = draw_passage_section(engine, x, y, direction, width, 4, psquare)
    if catch1[0] is False:
        return (True, (x, y, width, catch1[1]['blocks']))

    x0, y0 = catch1[1]['next_square']
    dx, dy = x0, y0
    catch = draw_passage_section(engine, x0, y0, direction, width, 2, psquare)
    if catch[0] is False:
        return (True, (x, y, width, []))

    x0, y0 = catch[1]['next_square']
    dx, dy = turn_across(dx, dy, direction, right(direction), width)
    engine.add(['door', 'passage', dx, dy, right(direction), 1, ('door', -1)])
    engine.add(['hall', 'passage', x0, y0, direction, width, psquare])
    return (True, (x, y, width, []))


# straight 20 ft, door to the left, 10 more feet & continue
def passage_table_4(engine, origin, x, y, direction, width, psquare, dice):
    catch1 = draw_passage_section(engine, x, y, direction, width, 4, psquare)
    if catch1[0] is False:
        return (True, (x, y, width, catch1[1]['blocks']))

    x0, y0 = catch1[1]['next_square']
    dx, dy = x0, y0
    catch = draw_passage_section(engine, dx, dy, direction, width, 2, psquare)
    if catch[0] is False:
        return (True, (x, y, width, []))

    x0, y0 = catch[1]['next_square']
    dx, dy = turn_across(dx, dy, direction, left(direction), width)
    engine.add(['door', 'passage', dx, dy, left(direction), 1, ('door', -1)])
    engine.add(['hall', 'passage', x0, y0, direction, width, psquare])
    return (True, (x, y, width, []))


# straight 20 ft, ends in door
def passage_table_5(engine, origin, x, y, direction, width, psquare, dice):
    catch = draw_passage_section(engine, x, y, direction, width, 4, psquare)
    if catch[0] is False:
        return (True, (x, y, width, catch[1]['blocks']))

    dx, dy = catch[1]['next_square']
    dx, dy = advance(dx, dy, turn_positive(direction),
                     middle_value(width, dice[0])-1)
    engine.add(['door', 'passage', dx, dy, direction, 1, ('door', -1)])
    return (True, (x, y, width, []))


# straight 20 ft, side passage right, 10 ft
# TODO: d12 for die 2 in passage generation dispatch?
def passage_table_6_7(engine, origin, x, y, direction, width, psquare, dice):
    catch1 = draw_passage_section(engine, x, y, direction, width, 4, psquare)
    if catch1[0] is False:
        return (True, (x, y, width, catch1[1]['blocks']))

    x0, y0 = catch1[1]['next_square']
    px, py = turn_across(x0, y0, direction, right(direction), width)
# TODO: add branching passage to immediate list, get width from dispatch
    nwidth = passage_width_table(dice[0])['width']
    catch = draw_passage_section(engine, x0, y0, direction,
                                 width, 2 + nwidth, psquare)
    if catch[0] is False:
        return (True, (x, y, width, []))

    nsquare = (psquare[0], -1)
    engine.add(['hall', 'passage', px, py, right(direction), nwidth, nsquare])
    x0, y0 = catch[1]['next_square']
    engine.add(['hall', 'passage', x0, y0, direction, width, psquare])
    return (True, (x, y, width, []))


# 20 feet forward, branch to left, 10 feet forward continue
def passage_table_8_9(engine, origin, x, y, direction, width, psquare, dice):
    catch1 = draw_passage_section(engine, x, y, direction, width, 4, psquare)
    if catch1[0] is False:
        return (True, (x, y, width, catch1[1]['blocks']))

    x0, y0 = catch1[1]['next_square']
    px, py = turn_across(x0, y0, direction, left(direction), width)
# TODO: add branching passag to immediate list, get width from dispatch
    nwidth = passage_width_table(dice[0])['width']
    catch = draw_passage_section(engine, x0, y0, direction,
                                 width, 2 + nwidth, psquare)
    if catch[0] is False:
        return (True, (x, y, width, []))

    x0, y0 = catch[1]['next_square']
    nsquare = (psquare[0], -1)
    engine.add(['hall', 'passage', px, py, left(direction), nwidth, nsquare])
    engine.add(['hall', 'passage', x0, y0, direction, width, psquare])
    return (True, (x, y, width, []))


# Straight 20ft, dead end, 10% chance of secret door
# 3rd die is d10
def passage_table_10(engine, origin, x, y, direction, width, psquare, dice):
    catch = draw_passage_section(engine, x, y, direction, width, 4, psquare)
    if catch[0] is False:
        return (True, (x, y, width, catch[1]['blocks']))

    if dice[1] >= 18:
        dx, dy = catch[1]['next_square']
        dx, dy = advance(dx, dy, turn_positive(direction),
                         middle_value(width, dice[0])-1)
        engine.add(['door', 'passage_secret', dx, dy,
                   direction, 1, ('door', -1)])
    return (True, (x, y, width, []))


# Straight 20ft, left turn, 10 ft
def passage_table_11_12(engine, origin, x, y, direction, width, psquare, dice):
    catch1 = draw_passage_section(engine, x, y, direction, width, 4, psquare)
    if catch1[0] is False:
        return (True, (x, y, width, catch1[1]['blocks']))

    px, py = catch1[1]['next_square']
    catch = draw_passage_section(engine, px, py, direction,
                                 width, width, psquare)

    if catch[0] is False:
        return (True, (x, y, width, []))

    # funky math to figure out turn coordinates
    if not is_positive(direction):
        px, py = catch[1]['next_square']
        px, py = advance(px, py, back(direction), 1)
    px, py = turn_across(px, py, direction, left(direction), width)
    catch = draw_passage_section(engine, px, py, left(direction),
                                 width, 2, psquare)
    if catch[0] is False:
        return (True, (x, y, width, []))

    px, py = catch[1]['next_square']
    engine.add(['hall', 'passage', px, py, left(direction), width, psquare])
    return (True, (x, y, width, []))


# Straight 20ft, right turn, 10 ft
def passage_table_13_14(engine, origin, x, y, direction, width, psquare, dice):
    catch1 = draw_passage_section(engine, x, y, direction, width, 4, psquare)
    if catch1[0] is False:
        return (True, (x, y, width, catch1[1]['blocks']))

    px, py = catch1[1]['next_square']
    catch = draw_passage_section(engine, px, py, direction,
                                 width, width, psquare)
    if catch[0] is False:
        return (True, (x, y, width, []))

    if not is_positive(direction):
        px, py = catch[1]['next_square']
        px, py = advance(px, py, back(direction), 1)
    px, py = turn_across(px, py, direction, right(direction), width)
    catch = draw_passage_section(engine, px, py, right(direction),
                                 width, 2, psquare)
    if catch[0] is False:
        return (True, (x, y, width, []))

    px, py = catch[1]['next_square']
    engine.add(['hall', 'passage', px, py, right(direction),
                width, psquare])
    return (True, (x, y, width, []))


def passage_table_15_19(engine, origin, x, y, direction, width, psquare, dice):
    engine.immediate_add(['room', origin, x, y, direction,
                         width, ("room", -1)])
    ret = engine.dispatch_immediate()
    return ret


# TODO: implement & enable stairs
# def passage_table_20(engine, origin, x, y, direction, width, psquare, dice):
#    engine.add(['stairs', 'passage', x, y, direction, width, psquare])


# TODO: width should be 12 or 20, reflecting which die to use on the table
# rather than relying on the creation of the element to set the width.
def dispatch_passage(engine, element, dice):
    origin = element[1]
    x = element[2]
    y = element[3]
    direction = element[4]
    width = element[5]
    psquare = element[6]
    if psquare[1] == -1:
        # TODO: add new passage to roomlist
        pass
    die_roll = dice[0]
    dice = dice[1:]

    # if the origin is a door, and the die roll says draw a passage, then
    # check for placement and move to the position
    if origin == "door" and die_roll <= 14:
        x, y, width = place_door_pass(engine, x, y, direction, width, dice)
        engine.log(":: placing passage from door\n\t{}, {}, {}".
                   format(x, y, width))
        if x is False:
            return (False,)

    # a hack, width is a tuple of (w x l)
    if element[1] == "draw":
        draw_passage_section(engine, origin, x, y, direction, *width, psquare)

    elif die_roll <= 2:
        return passage_table_1_2(engine, origin, x, y,
                                 direction, width, psquare, dice)
    elif die_roll <= 3:
        return passage_table_3(engine, origin, x, y,
                               direction, width, psquare, dice)
    elif die_roll <= 4:
        return passage_table_4(engine, origin, x, y,
                               direction, width, psquare, dice)
    elif die_roll <= 5:
        return passage_table_5(engine, origin, x, y,
                               direction, width, psquare, dice)
    elif die_roll <= 7:
        return passage_table_6_7(engine, origin, x, y,
                                 direction, width, psquare, dice)
    elif die_roll <= 9:
        return passage_table_8_9(engine, origin, x, y,
                                 direction, width, psquare, dice)
    elif die_roll <= 10:
        return passage_table_10(engine, origin, x, y,
                                direction, width, psquare, dice)
    elif die_roll <= 12:
        return passage_table_11_12(engine, origin, x, y,
                                   direction, width, psquare, dice)
    elif die_roll <= 14:
        return passage_table_13_14(engine, origin, x, y,
                                   direction, width, psquare, dice)
    elif die_roll <= 19:
        return passage_table_15_19(engine, origin, x, y,
                                   direction, width, psquare, dice)
    # else:
    #    passage_table_20(engine, origin, x, y,
    #                     direction, width, psquare, dice)


# allocate new identifier for descriptor table, add description
# worlds of potential here
def new_passage_descriptor():
    return 1


def dispatch_door(maparray, mapset, element, die_roll1=1, die_roll2=1):
    if maparray[element[2], element[3]] == ('void', 0):
        maparray[element[2], element[3]] = ('door', 1)

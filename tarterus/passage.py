from tarterus.maparray import MapArray
from tarterus.graphpaper import vector, right, left, back, turn_positive, is_positive, turn_across, advance, empty, middle_value
from random import randint

# hall origin into box dimensions for maparray ranges
# width always measures in a positive direction
def coords(x, y, direction, width, length):
    if direction == "n":
        return_val = {
                "x1" : x,
                "x2" : x + width,
                "w" :  width,
                "y1" : y - length + 1,
                "y2" : y + 1,
                "h" :  length,
                "nx" : x,
                "ny" : y - length,
                }
    elif direction == "e":
        return_val = {
                "x1" : x,
                "x2" : x + length,
                "w" :  length,
                "y1" : y,
                "y2" : y + width,
                "h" :  width,
                "nx" : x + length,
                "ny" : y
                }
    elif direction == "s":
        return_val = {
                "x1" : x,
                "x2" : x + width,
                "w" :  width,
                "y1" : y,
                "y2" : y + length,
                "h" :  length,
                "nx" : x,
                "ny" : y + length
                }
    elif direction == "w":
        return_val = {
                "x1" : x - length + 1,
                "x2" : x + 1,
                "w" :  length,
                "y1" : y,
                "y2" : y + width,
                "h" :  width,
                "nx" : x - length,
                "ny" : y
                }
    return return_val
# current behavior is to draw a passage until it hits non-void tiles
# TODO: COLUMN MODES

def draw_passage_section(maparray, x, y, direction, width, length, psquare):
    origins = [(x, y)]
    d_vec = vector(direction)
    o_vec = vector(turn_positive(direction))
    for i in range(1, width):
        origins.append((x + i * o_vec[0], y + i * o_vec[1]))
    blocks = []
    step_out = False # after the first block is hit, the rest of the
                         # passage advances one more step then the process
                         # terminates
    for i in range(length):
        for s in origins:
            target = (s[0] + i * d_vec[0], s[1] + i * d_vec[1])
            if maparray[target[0], target[1]] != ('void', 0):
                origins.remove(s)
                blocks.append(s)
            elif target[0] <= 0 or target[0] + 1 >= maparray.w or \
                    target[1] <= 0 or target[1] + 1 >= maparray.h:
                return { "result" : "edge", "blocks" : [] }
            else:
                maparray[target[0], target[1]] = psquare
        if step_out is True:
            break
        if len(origins) < width:
            step_out = True
    if len(blocks) > 0:
        return {"result" : "blocked", "blocks": blocks}
    else:
        return { "result" : "success", 
                "next_square": (x + length * d_vec[0], y + length * d_vec[1]) }
# draw a passage if it is an entirely clear path
# TODO (if needed): return more meaningful blocks data
def passage_no_block(maparray, x, y, direction, width, length, psquare):
    c = coords(x, y, direction, width, length)
    if empty(maparray, c['x1'], c['y1'], c['w'], c['h']):
        maparray[c['x1']:c['x2'], c['y1']:c['y2']] = psquare
        return { "result" : "success",
                "next_saure" : (c['nx'], c['ny'])
                }
    else:
        return { "result" : "blocked", "blocks" : [] }


# TODO columns
# dieroll = -1 : d12 (passage from passage)
# dieroll = 20 : d20 (passage from chamber)
def passage_width_table(die_roll = -1, from_chamber = False):
    if die_roll == -1:
        die_roll = randint(1, 12)
    elif die_roll == 20:
        die_roll = randint(1, 20)
        
    if die_roll <= 2:
        return {"width" : 1}
    elif die_roll <= 12:
        return {"width" : 2}
    elif die_roll <= 14:
        return {"width" : 4}
    elif die_roll <= 16:
        return {"width" : 6}
    else:
        return {"width" : 8}

# straight 30ft, no doors or side passages 10 more feet & continue
def passage_table_1_2(maparray, mapset, x, y, direction, width, psquare, die_roll=-1):
    catch = draw_passage_section(maparray, x, y, direction, width, 6, psquare)
    if catch['result'] == 'success':
        nx = catch['next_square'][0]
        ny = catch['next_square'][1]
        mapset.add(('hall', 'passage', nx, ny, direction, width, psquare))
        return None
    else:
        return catch['blocks']

# for positioning doors & side passages one back from next_square and possibly
# across (width) tiles

# straight 20 ft, door to the right, 10 more feet & continue
def passage_table_3(maparray, mapset, x, y, direction, width, psquare, die_roll=-1):
    catch = draw_passage_section(maparray, x, y, direction, width, 4, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    x, y = catch['next_square']
    dx, dy = x, y
    catch = draw_passage_section(maparray, x, y, direction, width, 2, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    x, y = catch['next_square']
    dx, dy = turn_across(x, y, direction, right(direction), width)
    mapset.add(('door', 'passage', dx, dy, right(direction), 1, ('door', -1)))
    mapset.add(('hall', 'passage', x, y, direction, width, psquare))
    return None

# straight 20 ft, door to the left, 10 more feet & continue
def passage_table_4(maparray, mapset, x, y, direction, width, psquare, die_roll=-1):
    catch = draw_passage_section(maparray, x, y, direction, width, 4, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    x, y = catch['next_square']
    dx, dy = x, y
    catch = draw_passage_section(maparray, x, y, direction, width, 2, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    x, y = catch['next_square']
    dx, dy = turn_across(x, y, direction, left(direction), width)
    mapset.add(('door', 'passage', dx, dy, left(direction), 1, ('door', -1)))
    mapset.add(('hall', 'passage', x, y, direction, width, psquare))
    return None

# straight 20 ft, ends in door 
def passage_table_5(maparray, mapset, x, y, direction, width, psquare, die_roll=-1):
    catch = draw_passage_section(maparray, x, y, direction, width, 4, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    dx, dy = catch['next_square']
    dx, dy = advance(dx, dy, turn_positive(direction), middle_value(width, die_roll)-1)
    mapset.add(('door', 'passage', dx, dy, direction, 1, ('door', 1)))
    return None

# straight 20 ft, side passage right, 10 ft
def passage_table_6_7(maparray, mapset, x, y, direction, width, psquare, die_roll=-1):
    catch = draw_passage_section(maparray, x, y, direction, width, 4, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    x, y = catch['next_square']
    # px, py = back_to_right(x, y, direction, width)
    px, py = advance(x, y, back(direction), 1)
    px, py = turn_across(px, py, direction, right(direction), width)
    nwidth = passage_width_table(die_roll)['width']
    nsquare = (psquare[0], new_passage_descriptor())
    mapset.add(('hall', 'passage', px, py, right(direction), nwidth, nsquare))
    catch = draw_passage_section(maparray, x, y, direction, width, 2, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    x, y = catch['next_square']
    mapset.add(('hall', 'passage', x, y, direction, width, psquare))
    return None

# 20 feet forward, branch to left, 10 feet forward continue
def passage_table_8_9(maparray, mapset, x, y, direction, width, psquare, die_roll=-1):
    catch = draw_passage_section(maparray, x, y, direction, width, 4, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    x, y = catch['next_square']
    # px, py = back_to_left(x, y, direction, width)
    px, py = advance(x, y, back(direction), 1)
    px, py = turn_across(px, py, direction, left(direction), width)
    nwidth = passage_width_table(die_roll)['width']
    nsquare = (psquare[0], new_passage_descriptor())
    mapset.add(('hall', 'passage', px, py, left(direction), nwidth, nsquare))
    catch = draw_passage_section(maparray, x, y, direction, width, 2, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    x, y = catch['next_square']
    mapset.add(('hall', 'passage', x, y, direction, width, psquare))
    return None

# Straight 20ft, dead end, 10% chance of secret door
def passage_table_10(maparray, mapset, x, y, direction, width, psquare, die_roll=-1):
    catch = draw_passage_section(maparray, x, y, direction, width, 4, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    x, y = catch['next_square']
    if die_roll >= 19:
        dx, dy = catch['next_square']
        dx, dy = advance(dx, dy, turn_positive(direction), middle_value(width, die_roll)-1)
        mapset.add(('door', 'passage', dx, dy, direction, 1, ('door', 1)))
    return None

# Straight 20ft, left turn, 10 ft
def passage_table_11_12(maparray, mapset, x, y, direction, width, psquare, die_roll=-1):
    catch = draw_passage_section(maparray, x, y, direction, width, 4, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    px, py = catch['next_square']
    catch = draw_passage_section(maparray, px, py, direction, width, width, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    if not is_positive(direction):
        px, py = catch['next_square']
        px, py = advance(px, py, back(direction), 1)
    px, py = turn_across(px, py, direction, left(direction), width)
    catch = draw_passage_section(maparray, px, py, left(direction), width, 2, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    px, py = catch['next_square']
    mapset.add(('hall', 'passage', px, py, left(direction), width, psquare))
    return None


def passage_table_13_14(maparray, mapset, x, y, direction, width, psquare, die_roll=-1):
    catch = draw_passage_section(maparray, x, y, direction, width, 4, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    px, py = catch['next_square']
    catch = draw_passage_section(maparray, px, py, direction, width, width, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    if not is_positive(direction):
        px, py = catch['next_square']
        px, py = advance(px, py, back(direction), 1)
    px, py = turn_across(px, py, direction, right(direction), width)
    catch = draw_passage_section(maparray, px, py, right(direction), width, 2, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    px, py = catch['next_square']
    mapset.add(('hall', 'passage', px, py, right(direction), width, psquare))
    return None


def passage_table_15_19(maparray, mapset, x, y, direction, width, psquare, die_roll=-1):
    mapset.add(('room', 'passage', x, y, direction, width, psquare))


def passage_table_20(maparray, mapset, x, y, direction, width, psquare, die_roll=-1):
    mapset.add(('stairs', 'passage', x, y, direction, width, psquare))


def dispatch_passage(maparray, mapset, element, die_roll, die_roll2):
    x = element[2]
    y = element[3]
    direction = element[4]
    width = element[5]
    psquare = element[6]
    if psquare[1] == -1:
        width = passage_width_table(die_roll2)
        # add new passage to roomlist
    if die_roll <= 2:
        passage_table_1_2(maparray, mapset, x, y, direction, width, psquare, die_roll2)
    elif die_roll <= 3:
        passage_table_3(maparray, mapset, x, y, direction, width, psquare, die_roll2)
    elif die_roll <= 4:
        passage_table_4(maparray, mapset, x, y, direction, width, psquare, die_roll2)
    elif die_roll <= 5:
        passage_table_5(maparray, mapset, x, y, direction, width, psquare, die_roll2)
    elif die_roll <= 7:
        passage_table_6_7(maparray, mapset, x, y, direction, width, psquare, die_roll2)
    elif die_roll <= 9:
        passage_table_8_9(maparray, mapset, x, y, direction, width, psquare, die_roll2)
    elif die_roll <= 10:
        passage_table_10(maparray, mapset, x, y, direction, width, psquare, die_roll2)
    elif die_roll <= 12:
        passage_table_11_12(maparray, mapset, x, y, direction, width, psquare, die_roll2)
    elif die_roll <= 14:
        passage_table_13_14(maparray, mapset, x, y, direction, width, psquare, die_roll2)
    elif die_roll <= 19:
        passage_table_15_19(maparray, mapset, x, y, direction, width, psquare, die_roll2)
    else:
        passage_table_20(maparray, mapset, x, y, direction, width, psquare, die_roll2)

# allocate new identifier for descriptor table, add description
# worlds of potential here
def new_passage_descriptor():
    return 1 


def dispatch_door(maparray, mapset, element, die_roll1=1, die_roll2=1):
    if maparray[element[2], element[3]] == ('void', 0):
        maparray[element[2], element[3]] = ('door', 1)

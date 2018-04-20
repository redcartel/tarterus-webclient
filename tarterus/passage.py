from tarterus.maparray import MapArray
from random import randint

def vector(direction):
    return_val = {
            'n' : (0, -1),
            'e' : (1, 0),
            's' : (0, 1),
            'w' : (-1, 0)
        }
    return return_val[direction]


def right(direction):
    return_val = {
            'n' : 'e',
            'e' : 's',
            's' : 'w',
            'w' : 'n'
        }
    return return_val[direction]


def left(direction):
    return_val = {
            'n' : 'w',
            'e' : 'n',
            's' : 'e',
            'w' : 's'
        }
    return return_val[direction]


def back(direction):
    return_val = {
            'n' : 's',
            'e' : 'w',
            's' : 'n',
            'w' : 'e'
        }
    return return_val[direction]


# turn to the orthogonal direction that is numerically positive along the 
# x or y axis
def turn_positive(direction):
    return_val = {
            'n' : 'e',
            'e' : 's',
            's' : 'e',
            'w' : 's'
        }
    return return_val[direction]


def back_to_left(x, y, direction, width):
    x, y = advance(x, y, back(direction), 1) # take one step back
    if left(direction) == turn_positive(direction): # cross width of the hall
        x, y = advance(x, y, left(direction), width)
    else: # one square to left
        x, y = advance(x, y, left(direction), 1)
    return (x, y)


def back_to_right(x, y, direction, width):
    x, y = advance(x, y, back(direction), 1) # take one step back
    if right(direction) == turn_positive(direction): # cross width of the hall
        x, y = advance(x, y, right(direction), width)
    else: # one square to right
        x, y = advance(x, y, right(direction), 1)
    return (x, y)


def advance(x, y, direction, length):
    return (x + vector(direction)[0] * length, 
            y + vector(direction)[1] * length)


def empty(maparray, x, y, w, h):
    return all(s == ('void', 0) for s in maparray.squares(x, y, w, h))


def middle_value(n, roll=-1):
    if n % 2 == 1:
        return n // 2 + 1
    elif roll == -1:
        return n // 2 + randint(0,1)
    else:
        return n // 2 + roll


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
def passage_width_table(die_roll, from_chamber = False):
    if from_chamber is True:
        n = (die_roll - 1) % 20 + 1
    else:
        n = (die_roll - 1) % 12 + 1
    if n <= 2:
        return {"width" : 1}
    elif n <= 12:
        return {"width" : 2}
    elif n <= 14:
        return {"width" : 4}
    elif n <= 16:
        return {"width" : 6}
    else:
        return {"width" : 8}

# straight 30ft, no doors or side passages 10 more feet & continue
def passage_table_1_2(maparray, mapset, x, y, direction, width, psquare):
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
def passage_table_3(maparray, mapset, x, y, direction, width, psquare):
    catch = draw_passage_section(maparray, x, y, direction, width, 4, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    x, y = catch['next_square']
    dx, dy = back_to_right(x, y, direction, width)
    mapset.add(('door', 'passage', dx, dy, right(direction), 1, ('door', -1)))
    catch = draw_passage_section(maparray, x, y, direction, width, 2, psquare)
    x, y = catch['next_square']
    mapset.add(('hall', 'passage', x, y, direction, width, psquare))
    return None

# straight 20 ft, door to the left, 10 more feet & continue
def passage_table_4(maparray, mapset, x, y, direction, width, psquare):
    catch = draw_passage_section(maparray, x, y, direction, width, 4, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    x, y = catch['next_square']
    dx, dy = back_to_left(x, y, direction, width)
    mapset.add(('door', 'passage', dx, dy, left(direction), width, ('door', -1)))
    catch = draw_passage_section(maparray, x, y, direction, width, 2, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    x, y = catch['next_square']
    mapset.add(('hall', 'passage', x, y, direction, width, psquare))
    return None

# straight 20 ft, ends in door
def passage_table_5(maparray, mapset, x, y, direction, width, psquare):
    catch = draw_passage_section(maparray, x, y, direction, width, 4, psquare)
    if catch['result'] != 'success':
        return catch['blocks']
    dx, dy = catch['next_square']
    dx, dy = advance(dx, dy, turn_positive(direction), middle_value(width)-1)
    mapset.add(('door', 'passage', dx, dy, direction, 1, psquare))
    return None

def dispatch_passage(maparray, mapset, element, die_roll = -1, die_roll2 = -1):
    if die_roll == -1:
        die_roll = randint(1,5)
    die_roll = (die_roll - 1) % 20 + 1
    if die_roll2 == -2:
        die_roll2 = randint(1,12)
    die_roll2 = (die_roll2 - 1) % 20 + 1
    x = element[2]
    y = element[3]
    direction = element[4]
    width = element[5]
    psquare = element[6]
    if psquare[1] == -1:
        width = passage_width_table(die_roll2)
        # add new passage to roomlist
    if die_roll <= 2:
        passage_table_1_2(maparray, mapset, x, y, direction, width, psquare)
    elif die_roll <= 3:
        passage_table_3(maparray, mapset, x, y, direction, width, psquare)
    elif die_roll <= 4:
        passage_table_4(maparray, mapset, x, y, direction, width, psquare)
    else:
        passage_table_5(maparray, mapset, x, y, direction, width, psquare)

def dispatch_door(maparray, mapset, element):
    if maparray[element[2], element[3]] == ('void', 0):
        maparray[element[2], element[3]] = ('door', 1)

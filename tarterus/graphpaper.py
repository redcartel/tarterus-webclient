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


def is_positive(direction):
    return_val = {
            'n' : False,
            'e' : True,
            's' : True,
            'w' : False
        }
    return return_val[direction]


# the location of a branch of a passage of a given width. the turn may or may
# not result in the new branch being across the hall vs. 1 square away, depend-
# ing on if the turn is in a positive or negative coordinate direction
def turn_across(x, y, direction, new_direction, width):
    if turn_positive(direction) == new_direction:
        return advance(x, y, new_direction, width)
    if turn_positive(direction) == back(new_direction):
        return advance(x, y, new_direction, 1)


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
        return n // 2 + (roll % 2)



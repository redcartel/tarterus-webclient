
def vector(direction):
    return_val = {
            'n': (0, -1),
            'e': (1, 0),
            's': (0, 1),
            'w': (-1, 0)
        }
    return return_val[direction]


def right(direction):
    return_val = {
            'n': 'e',
            'e': 's',
            's': 'w',
            'w': 'n'
        }
    return return_val[direction]


def left(direction):
    return_val = {
            'n': 'w',
            'e': 'n',
            's': 'e',
            'w': 's'
        }
    return return_val[direction]


def back(direction):
    return_val = {
            'n': 's',
            'e': 'w',
            's': 'n',
            'w': 'e'
        }
    return return_val[direction]


# turn to the orthogonal direction that is numerically positive along the
# x or y axis
def turn_positive(direction):
    return_val = {
            'n': 'e',
            'e': 's',
            's': 'e',
            'w': 's'
        }
    return return_val[direction]


def is_positive(direction):
    return_val = {
            'n': False,
            'e': True,
            's': True,
            'w': False
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


def gt_or_eq(p1, p2, direction):
    if direction == "n":
        return p1[1] <= p2[1]
    elif direction == "e":
        return p1[0] >= p2[0]
    elif direction == "s":
        return p1[1] >= p2[1]
    elif direction == "w":
        return p1[0] <= p1[0]


def empty(maparray, x, y, w, h):
    return all(s == ('void', 0) for s in maparray.squares(x, y, w, h))


def middle_value(n, roll):
    if n % 2 == 1:
        return n // 2 + 1
    else:
        return n // 2 + (roll % 2)


def distance(s1, s2):
    if s1[0] == s2[0]:
        if s2[1] - s1[1] >= 0:
            return s2[1] - s1[1]
        else:
            return None

    elif s1[1] == s2[1]:
        if s2[0] - s1[0] >= 0:
            return s2[0] - s1[0]
        else:
            return None

    else:
        return None

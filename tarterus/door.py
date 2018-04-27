from tarterus.graphpaper import vector, right, left, back, turn_positive
from tarterus.graphpaper import is_positive, turn_across
from tarterus.graphpaper import advance, middle_value  # , empty
from tarterus.passage import passage_width_table

DICE_ARRAY = [20, 20, 12]

def position_hall(maparray, origin, x, y, direction, dice):
    # big passages from rooms
    if origin == "room":
        die = dice[0]
        other_die = dice[1]
    # smaller ones from other passages
    else:
        die = dice[1]
        other_die = dice[0]
    # determine offset for middle_value
    if die % 2 == 0:
        mid_die = 0
    else:
        mid_die = 1
    # search left or right from center position?
    if other_die % 2 == 0:
        delta = 1
    else:
        delta = -1
    width = passage_width_table(die)['width']
    while width > 0:
        if width == 1:
            x0, y0 = advance(x, y, direction, 1)
            if maparray[x, y][0] != "void":
                return False, False, False
            else:
                return x0, y0, 1
        else:
            offset = middle_value(width, mid_die) % width
            end_offset = (offset + delta) % width
            while offset != end_offset:
                x0, y0 = advance(x, y, direction, 1)
                x0, y0 = advance(x0, y0, back(turn_positive(direction)),
                                              width-1)
                x0, y0 = advance(x0, y0, turn_positive(direction), offset)
                works = True
                for i in range(width):  
                    x1, y1 = advance(x0, y0, turn_positive(direction), i)
                    if maparray[x1, y1][0] != "void":
                        works = False
                        break
                if works == True:
                    return x0, y0, width
                else:
                    offset = (offset + delta) % width
            if width > 2:
                width = width - 2
            else:
                width = width - 1


def dispatch_door():
    pass

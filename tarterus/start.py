from tarterus.maparray import MapArray
from tarterus.room import room
# from random import randint

DICE_ARRAY = [2, 20, 20]


def start_table_1(engine, origin, dice):
    layout = MapArray(('void', 0), (10, 10))
    layout[4:6, 0:2] = ('hall', 1)
    layout[8:10, 4:6] = ('hall', 2)
    layout[4:6, 8:10] = ('hall', 3)
    layout[0:2, 4:6] = ('hall', 4)
    layout[2, 3] = ('vwal', 5)
    layout[2, 6] = ('vwal', 5)
    layout[7, 3] = ('vwal', 5)
    layout[7, 6] = ('vwal', 5)
    layout[3, 2] = ('hwal', 5)
    layout[6, 2] = ('hwal', 5)
    layout[3, 7] = ('hwal', 5)
    layout[6, 7] = ('hwal', 5)
    layout[2, 2] = ('tcor', 5)
    layout[7, 2] = ('tcor', 5)
    layout[2, 7] = ('bcor', 5)
    layout[7, 7] = ('bcor', 5)
    layout[2, 4:6] = ('open', 5)
    layout[4:6, 2] = ('open', 5)
    layout[7, 4:6] = ('open', 5)
    layout[4:6, 7] = ('open', 5)
    layout[3:7, 3:7] = ('room', 5)
    layout[5, 5] = ('stup', 5)
    w = 10
    h = 10
    if origin not in ['n', 'e', 's', 'w', 'm']:
        origin = 'm'
    if origin == 'n':
        x = engine.maparray.w // 2 - w // 2
        y = 0
    elif origin == 'e':
        x = engine.maparray.w - w
        y = engine.maparray.h // 2 - h // 2
    elif origin == 's':
        x = engine.maparray.w // 2 - w // 2
        y = engine.maparray.h - h
    elif origin == 'w':
        x = 0
        y = engine.maparray.h // 2 - h // 2
    elif origin == 'm':
        x = engine.maparray.w // 2 - w // 2
        y = engine.maparray.h // 2 - h // 2

    engine.generate_description(('hall', 1))
    engine.describe(1, {'type': 'passage',
                        'w': 10})
    engine.generate_description(('hall', 2))
    engine.describe(2, {'type': 'passage',
                        'w': 10})
    engine.generate_description(('hall', 3))
    engine.describe(3, {'type': 'passage',
                        'w': 10})
    engine.generate_description(('hall', 4))
    engine.describe(4, {'type': 'passage',
                        'w': 10})
    engine.generate_description(('hall', 5))
    engine.describe(5, {'type': 'chamber', 'w': 20, 'h': 20})

    if origin != 'n':
        engine.add(['hall', 'passage', x+4, y-1, 'n', 2, ('hall', 1)])

    if origin != 'e':
        engine.add(['hall', 'passage', x+10, y+4, 'e', 2, ('hall', 2)])

    if origin != 's':
        engine.add(['hall', 'passage', x+4, y+10, 's', 2, ('hall', 3)])

    if origin != 'w':
        engine.add(['hall', 'passage', x-1, y+4, 'w', 2, ('hall', 4)])

    engine.maparray[x:x+w, y:y+h] = layout
    return (True,)


def start_table_2(engine, origin, dice):
    engine.log(":: start_table_2")
    layout = room(6, 6, ('room', 1))
    layout[3, 3] = ('stup', 1)
    w = 6
    h = 6
    if origin not in ['n', 'e', 's', 'w', 'm']:
        origin = 'm'
    if origin == 'n':
        d = 'n'
        x = engine.maparray.w // 2 - w // 2
        y = 4
        engine.maparray[x:x+w, y:y+h] = layout
        x0 = engine.maparray.w // 2 - 1
        y0 = 0
        engine.maparray[x0:x0+2, y] = ('open', 1)
        engine.maparray[x0:x0+2, 0:y] = ('hall', 2)
    elif origin == 'e':
        d = 'e'
        x = engine.maparray.w - w - 4
        y = engine.maparray.h // 2 - h // 2
        engine.maparray[x:x+w, y:y+h] = layout
        x0 = engine.maparray.w - 4
        y0 = engine.maparray.h // 2 - 1
        engine.maparray[x0-1, y0:y0+2] = ('open', 1)
        engine.maparray[x0:engine.maparray.w, y0:y0+2] = ('hall', 2)
    elif origin == 's':
        d = 's'
        x = engine.maparray.w // 2 - w // 2
        y = engine.maparray.h - h - 4
        engine.maparray[x:x+w, y:y+h] = layout
        x0 = engine.maparray.w // 2 - 1
        y0 = engine.maparray.h - 4
        engine.maparray[x0:x0+2, y0-1] = ('open', 1)
        engine.maparray[x0:x0+2, y0:y0+4] = ('hall', 2)
    elif origin == 'w':
        d = 'w'
        x = 4
        y = engine.maparray.h // 2 - h // 2
        engine.maparray[x:x+w, y:y+h] = layout
        x0 = 0
        y0 = engine.maparray.h // 2 - 1
        engine.maparray[x, y0:y0+2] = ('open', 1)
        engine.maparray[x0:x0+4, y0:y0+2] = ('hall', 2)
    elif origin == 'm':
        d = ['n', 'e', 's', 'w'][dice[0] % 4]
        engine.log("\td={}".format(d))
        x = engine.maparray.w // 2 - w // 2
        y = engine.maparray.h // 2 - h // 2
        engine.maparray[x:x+w, y:y+h] = layout
        if d == 'n':
            engine.maparray[x+2:x+4, y] = ('open', 1)
            engine.add(['hall', 'exit', x+2, y-1, 'n', 2, ('hall', -1)])
        elif d == 'e':
            engine.maparray[x+w-1, y+2:y+4] = ('open', 1)
            engine.add(['hall', 'exit', x+w, y+2, 'e', 2, ('hall', -1)])
        elif d == 's':
            engine.maparray[x+2:x+4, y+h-1] = ('open', 1)
            engine.add(['hall', 'exit', x+2, y+h, 's', 2, ('hall', -1)])
        elif d == 'w':
            engine.maparray[x, y+2:y+4] = ('open', 1)
            engine.add(['hall', 'exit', x-1, y+2, 'w', 2, ('hall', -1)])

    engine.generate_description(('room', 1))
    engine.describe(1, {'type': 'chamber',
                        'w': 20, 'h': 20})
    engine.generate_description(('hall', 2))
    engine.describe(2, {'type': 'passage',
                        'w': 10})
    directions = ['n', 'e', 's', 'w']
    directions.remove(d)
    i = dice[1] % 3
    i2 = (dice[0] + dice[1]) % 2
    d0 = directions[i]
    directions.remove(d0)
    d1 = directions[i2]
    ds = [d0, d1]
    engine.log("\tds={}".format(ds))
    for d in ds:
        if d == 'n':
            engine.add(['door', 'exit', x+3, y, 'n', 1, ('door', -1)])
        elif d == 'e':
            engine.add(['door', 'exit', x+w-1, y+3, 'e', 1, ('door', -1)])
        elif d == 's':
            engine.add(['door', 'exit', x+3, y+h-1, 's', 1, ('door', -1)])
        elif d == 'w':
            engine.add(['door', 'exit', x, y+3, 'w', 1, ('door', -1)])
    return (True,)


def start_table_3(engine, origin, dice):
    pass


def dispatch_start(engine, element, dice):
    origin = element[1]["origin"]
    die = dice[0]
    dice = dice[1:]

    if die <= 1:
        return start_table_1(engine, origin, dice)
    elif die <= 2:
        return start_table_2(engine, origin, dice)

from tarterus.graphpaper import right, left, back #turn_positive
# from tarterus.graphpaper import is_positive, turn_across
from tarterus.graphpaper import advance  # , empty, middle_value
from tarterus.passage import passage_width_table
from tarterus.room import find_loc

# TODO: stairs & trapped doors
# TODO: "blocking void"
DICE_ARRAY = [18, 20, 12]


def is_simple(maparray, origin, x, y, direction):
    forbidden_tiles = ['bcor', 'tcor']

    x0, y0 = advance(x, y, direction, 1)
    if x0 <= 1 or x0 + 1 >= maparray.w:
        return "forbidden"
    elif y0 <= 1 or y0 + 1 >= maparray.h:
        return "forbidden"

    dsquare = maparray[x0, y0][0]
    if dsquare in forbidden_tiles:
        return "forbidden"
    elif dsquare == "void":
        return "void"
    elif dsquare in ['hwal', 'vwal']:
        return "wall"
    else:
        return "simple"


# TODO: passages from actual door table
# def table_passage(engine, origin, x, y, direction, width, dsquare, dice):
#     engine.log(":: door: table_passage")
#     simp = is_simple(engine.maparray, origin, x, y, direction)
#     if simp == "forbidden":
#         return (False,)
#     # if the next tile is a wall, make two doors back to back
#     elif simp == "wall":
#         engine.maparray[x, y] = dsquare
#         x0, y0 = advance(x, y, direction, 1)
#         engine.immediate_add(['door', 'door', x0, y0,
#                              direction, 1, (dsquare[0], -1)])
#         engine.dispatch_immediate()
#         return (True,)
#     # if the next tile is a room or hall floor, just connect the door
#     elif simp == "simple":
#         engine.maparray[x, y] = dsquare
#         return (True,)
#     # reach this point, other side is void
#     # TODO: table_width_passage, not so many 5' halls
#     width0 = passage_width_table(dice[1])['width']
#     engine.immediate_add(['hall', 'door', x, y,
#                           direction, width0, ('hall', -1)])
#     engine.log(":: immediate add hall from door")
#     if engine.dispatch_immediate()[0] is True:
#         engine.log("\tsuccess in table_passage")
#         engine.maparray[x, y] = dsquare
#         return (True,)
#     else:
#         engine.log("\tfail")
#         return (False,)


# test if a minimal room (20' x 20') will fit originating from the door
def room_will_fit(engine, x, y, direction):
    x, _ = find_loc(engine.maparray, x, y, 6, 6, direction, 1, [5, 6])
    engine.log(":: room_will_fit : {}, {}, {}".format(x, y, direction))
    if x is False:
        engine.log("\tfailed")
        return False
    else:
        engine.log("\tpassed")
        return True


# TODO: add priority elements to the engine queue, draw room immediately after
# the door
def table_chamber_9_18(engine, origin, x, y, direction, width, dsquare, dice):
    engine.log(":: door: table_room")
    if not room_will_fit(engine, x, y, direction):
        return (False,)
    else:
        engine.immediate_add(['room', 'door', x, y,
                              direction, 1, ('room', -1)])
        if engine.dispatch_immediate()[0] is True:
            engine.maparray[x, y] = dsquare
        else:
            return (False,)


# passage extends 10 feet, then T intersection 10 ft to left and to right
def table_passage_1_2(engine, origin, x, y, direction, width, dsquare, dice):
    engine.log(":: door: table_passage_1_2")
    if origin == "exit":
        width0 = passage_width_table(dice[0])['width']
    else:
        width0 = passage_width_table(dice[1])['width']
    engine.immediate_add(['hall', 'do12', x, y,
                          direction, width0, ('hall', -1)])
    ret = engine.dispatch_immediate()
    if ret[0] is True:
        engine.maparray[x, y] = dsquare
        return (True,)
    else:
        engine.log("\tfail")
        return (False,)


def table_passage_3_8(engine, origin, x, y, direction, width, dsquare, dice):
    engine.log(":: door: table_passage_1_2")
    if origin == "exit":
        width0 = passage_width_table(dice[0])['width']
    else:
        width0 = passage_width_table(dice[1])['width']
    engine.immediate_add(['hall', 'do38', x, y,
                          direction, width0, ('hall', -1)])
    ret = engine.dispatch_immediate()
    if ret[0] is True:
        engine.maparray[x, y] = dsquare
        return (True,)
    else:
        engine.log("\tfail")
        return (False,)


# draws a door if there is an immediate exit on the other side
# returns (a, b) a True if the door is drawn, if not, b is True if a further
# passage can be drawn
def simple_door(engine, origin, x, y, direction, width, dsquare, dice):
    simp = is_simple(engine.maparray, origin, x, y, direction)
    if simp == "forbidden":
        return (False, False)
    elif simp == "wall":
        x0, y0 = advance(x, y, direction, 1)
        engine.immediate_add(['door', 'door', x0, y0,
                              direction, 1, (dsquare[0], -1)])
        if engine.dispatch_immediate()[0] is True:
            engine.maparray[x, y] = dsquare
            return (True, True)
        else:
            return (False, False)
    elif simp == "simple":
        engine.maparray[x, y] = dsquare
        return (True, True)
    elif simp == "void":
        return (False, True)


def dispatch_door(engine, element, dice):
    origin = element[1]
    x = element[2]
    y = element[3]
    direction = element[4]
    if x <= 1 or x >= engine.maparray.w:
        return (False,)
    elif y <= 1 or y >= engine.maparray.h:
        return (False,)

    if engine.maparray[x, y][0] not in ["void", "vwal", "hwal"]:
        return (False,)

    # don't build doors next to doors or open spaces
    x0, y0 = advance(x, y, left(direction), 1)
    x1, y1 = advance(x, y, right(direction), 1)
    if engine.maparray[x0, y0][0] in ['room', 'door', 'hall', 'open']:
        return (False,)

    if engine.maparray[x1, y1][0] in ['room', 'door', 'hall', 'open']:
        return (False,)

    width = element[5]
    dsquare = element[6]
    die_roll = dice[0]
    dice = dice[1:]
    if dsquare[1] == -1:
        dsquare = engine.generate_description(dsquare)
        engine.describe(dsquare[1], {"type": "door",
                                     "d": direction})

    r1, r2 = simple_door(engine, origin, x, y, direction, width, dsquare, dice)
    if r1 is True:
        return (True,)
    elif r1 is False and r2 is False:
        return (False,)
    # (False, True) use normal tables

    if die_roll <= 2:
        return table_passage_1_2(engine, origin, x, y,
                                 direction, width, dsquare, dice)

    elif die_roll <= 8:
        return table_passage_3_8(engine, origin, x, y,
                                 direction, width, dsquare, dice)

    elif die_roll <= 18:
        return table_chamber_9_18(engine, origin, x, y,
                                  direction, width, dsquare, dice)


def describe_door(engine, d):
    dice = engine.roll([20, 20])
    door_description = door_type(dice, d['d'])
    return "A{}".format(door_description)


def door_type(dice, direction):
    dword = {"n": "north", "e": "east", "s": "south", "w": "west"}
    if dice[1] % 2 == 0:
        side = dword[direction]
    else:
        side = dword[back(direction)]
    
    if dice[1] // 2 >= 10:
        lockword = "locked from the "
    else:
        lockword = "barred from the "

    d_pass = dword[back(direction)] + " / " + dword[direction]
    die = dice[0]
    if die <= 10:
        return " wooden door going " + d_pass
    elif die <= 12:
        return " wooden door " + lockword + side
    elif die <= 13:
        return " stone door going " + d_pass
    elif die <= 14:
        return " stone door " + lockword + side
    elif die <= 15:
        return "n iron door going " + d_pass
    elif die <= 16:
        return "n iron door " + lockword + side
    elif die <= 17:
        return " portcullis going " + d_pass
    elif die <= 18:
        return " portcullis locked from the " + side
    elif die <= 19:
        return " secret door going " + d_pass
    elif die <= 20:
        return " secret door " + lockword + side

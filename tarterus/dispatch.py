from tarterus.maparray import MapArray
from tarterus.passage import dispatch_passage, dispatch_door
from random import randint
# from tarterus.room import dispatch_room, dispatch_stairs, grow_room, starting_area

def the_engine(parameters):
    w = parameters['w']
    h = parameters['h']
    # x = parameters['x']
    # y = parameters['y']
    maparray = MapArray(('void', 0), (w, h))
    mapset = set()
    yield (maparray, mapset, parameters)
    if len(mapset) == 0:
        mapset.add(('hall', 'void', 10, 20, 'n', 10, ('hall', 1)))
        mapset.add(('hall', 'void', 30, 20, 'e', 10, ('hall', 2)))
        mapset.add(('hall', 'void', 50, 20, 's', 10, ('hall', 3)))
        mapset.add(('hall', 'void', 78, 20, 'w', 10, ('hall', 4)))
    while len(mapset) > 0:
        dispatch(maparray, mapset, mapset.pop(), parameters)
        yield (maparray, mapset, parameters)

def dispatch(maparray, mapset, element, parameters):
    if element[0] == 'hall':
        die_roll1 = randint(1,20)
        die_roll2 = randint(1,20)
        dispatch_passage(maparray, mapset, element, die_roll1, die_roll2)
    if element[0] == 'door':
        die_roll1 = randint(1,20)
        die_roll2 = randint(1,20)
        dispatch_door(maparray, mapset, element, die_roll1, die_roll2)

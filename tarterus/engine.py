from tarterus.maparray import MapArray
from tarterus.passage import dispatch_passage  # , dispatch_door
from tarterus.passage import DICE_ARRAY as passage_dice
from random import randint
from tarterus.room import dispatch_room
from tarterus.room import DICE_ARRAY as room_dice
from tarterus.door import dispatch_door
from tarterus.door import DICE_ARRAY as door_dice
# dispatch_room, dispatch_stairs, grow_room, starting_area


# Engine(params)
#   - w,h: Required. x and y dimensions. Measured in 5 foot squares
#   -dont_terminate: Boolean, if True, loop engine forever. Used for
#       interactive mode
#   -max_steps: Max number of steps in a given auto generate request. used to
#       build map with a progress update & to avoid blocking the server with
#       an overlong call.
#   -pop_mode: Method used to pick next dungeon feature to be added. Default is
#       "random" to pick an element from the PendingList at random, other
#       options are "stack" and "queue" to always take newest or oldest item.
class Engine():

    def __init__(self, params):
        self.params = params
        self.log_messages = []
        self.process_params()

        self.maparray = MapArray(("void", 0), (self.w, self.h))
        self.loaded_dice = []
        self.descriptions = [{}]

        self.engine = self.the_engine()

    def process_params(self):
        self.w = self.params['w']
        self.h = self.params['h']
        self.pending = PendingList(self.params.get("pop_mode", "random"))
        if self.params.get("log", False) is True:
            self.log = self.yes_log
        else:
            self.log = self.no_log
        self.dont_terminate = self.params.get("dont_terminate", False)
        self.max_steps = self.params.get("max_steps", -1)

        self.log("::Parameters Loaded\n\t{}".format(self.params))

    # Coroutine generator. At each step returns the length of pending.
    # .__next__() will iterate the generation by popping an element from
    # pending and dispatching it. .send(command) will dispatch the command
    def the_engine(self):
        ret = len(self.pending)
        while True:
            command = yield ret  # PEP 342
            if command is None and len(self.pending) > 0:
                self.log(":: Step()")
                self.dispatch(self.pending.pop(), {})
                ret = len(self.pending)
            elif command is None and self.dont_terminate is False:
                self.log(":: No Action")
                return
            elif command is not None:
                self.log(":: Command:\n\t{}".format(command))
                ret = self.dispatch_command(command)

    # Default log function, does nothing
    def no_log(self, message):
        pass

    def yes_log(self, message):
        self.log_messages.append(message)

    def get_log(self):
        return self.log_messages

    def print_log(self, message):
        print(message)

    # Generate the map by looping through the engine with no commands. Does not
    # respect dont_terminate. Should never create an infinite loop.
    def gen_map(self):
        the_engine = self.the_engine()
        next(the_engine)
        for ndispatches in the_engine:
            if ndispatches == 0:
                break

    # iterate map generation one step with no command
    def step(self):
        return next(self.engine)

    # send a command to the engine
    def send(self, command):
        return self.engine.send(command)

    def add(self, element):
        self.log(":: Add\n\t{}".format(element))
        self.pending.add(element)

    # Create a list of die roll results from a vector of the numbers of sides
    # of each die. All random number generation in the map generation process
    # is handled by this method and in the random pop method of PendingList
    def roll(self, dice, forced_rolls=[]):
        ret = []
        for i, nsides in enumerate(dice):
            try:
                ret.append(forced_rolls[i])
            except IndexError:
                try:
                    ret.append(self.loaded_dice[0])
                    self.loaded_dice = self.loaded_dice[1:]
                except IndexError:
                    ret.append(randint(1, nsides))
        self.log("::Dice rolled\n\t{}".format(ret))
        return ret

    def dispatch(self, element, command={}):
        if element[0] == 'describe':
            pass

        if element[0] == 'door':
            pass
            # dice = self.roll(door_dice, command.get("dice", []))
            # dispatch_door(self, element, dice)

        if element[0] == 'hall':
            dice = self.roll(passage_dice, command.get("dice", []))
            self.log("::dispatch_passage\n\t{}".format(element))
            dispatch_passage(self, element, dice)

        if element[0] == 'populate':
            pass

        if element[0] == 'room':
            dice = self.roll(room_dice, command.get("dice", []))
            self.log("::dispatch_room\n\t{}".format(element))
            dispatch_room(self, element, dice)

        if element[0] == 'stairs':
            pass

    def __str__(self):
        return """Engine:
maparray:
{}
descriptions:
{}
pending elements:
{}""".format(self.maparray, self.descriptions, self.pending)


# COMMANDS
# ['step']                              pop an element & dispatch
# ['add', element]                      add an element to the list
# ['insert', index, element]            insert element at position in list
# ['execute', index]                    pop specific element & dispatch
# ['dispatch_with_command', command]    pop specific element & dispatch w/
#                                           a command parameter
# ['step_with_command', index, command] pop an element & dispatch w/ a
#                                           command parameter
# ['remove', index]                     remove an element from a location
# ['replace', index, command]           replace the element at a location
# ['clear']                             clear maparray, descriptions, and
#                                           parameters
# ['set_params']                        reset the parameters from initiation
# ['get']                               get {maparray, pending, descriptions
# ['in', element]                       boolean, if an element is in the
#                                           pending list
# ['load_dice', dice]                   add list of forced die rolls
# ['roll', sides]
# ['log', message]
# ['get_log']
    def dispatch_command(self, command):
        if command is None:
            pass
        elif command[0] == 'step':
            self.dispatch(self.pending.pop())
            return len(self.pending)

        elif command[0] == 'add':
            self.pending.add(command[1])
            return len(self.pending)

        elif command[0] == 'insert':
            self.pending.insert(command[1], command[2])
            return len(self.pending)

        elif command[0] == 'execute':
            self.dispatch(self.pending.ipop(command[1]), None)
            return len(self.pending)

        elif command[0] == 'step_with_command':
            self.dispatch(self.pending.pop(), command[1])
            return len(self.pending)

        elif command[0] == 'execute_with_command':
            self.dispatch(self.pending.ipop(command[1]), command[2])
            return len(self.pending)

        elif command[0] == 'remove':
            self.pending.ipop(command[1])
            return len(self.pending)

        elif command[0] == 'replace':
            self.pending[command[1]] = command[2]
            return len(self.pending)

        # Clears everything but the log
        elif command[0] == 'clear':
            self.log("\n\n:: CLEARING ENGINE")
            self.maparray = MapArray(('void', 0), (self.w, self.h))
            self.descriptions = []
            self.pending.clear()
            self.pending = PendingList(self.params.get("pop_mode", "random"))
            return None

        elif command[0] == 'set_params':
            self.params = command[1]
            self.process_params()
            return None

        elif command[0] == 'get' and len(command) == 1:
            return {
                    "maparray": self.maparray,
                    "descriptions": self.descriptions,
                    "pending": self.pending
                }

        elif command[0] == 'in':
            return command[1] in self.pending.items

        elif command[0] == 'load_dice':
            self.loaded_dice = command[1]
            return None

        elif command[0] == 'roll':
            try:
                return self.roll(command[1])
            except IndexError:
                return self.roll([20])

        elif command[0] == 'log':
            self.log(command[1])
            return None

        elif command[0] == 'get_log':
            return "\n".join(str(message) for message in self.get_log())

        # this will render the map pretty well non-functional as a map, should
        # move this into MapArray logic if it is kept at all, but it's a hack
        # for testing
        elif command[0] == 'place_grid':
            for x in range(1, self.w, 5):
                for y in range(1, self.w, 5):
                    if self.maparray[x, y][0] == "void":
                        self.maparray[x, y][0] = "grid"


# PendingList
# The list of features to be added to the map. The constructor sets a mode for
# popping the items from the list. The default is "random" which does what it
# says. "Stack grabs the most recently added element. Queue grabs the oldest
# element.
class PendingList:

    def __init__(self, mode="random"):
        if mode == "random":
            self.pop = self.random_pop
        if mode == "stack":
            self.pop = self.stack_pop
        if mode == "queue":
            self.pop = self.queue_pop
        if mode == "middle":
            self.pop = self.middle_pop
        self.items = list()

    def __getitem__(self, i):
        return self.items[i]

    def __len__(self):
        return len(self.items)

    def add(self, element):
        self.items.append(element)

    def insert(self, i, element):
        self.items.insert(i, element)

    # pop the element at index i.
    def ipop(self, i):
        return self.items.pop(i)

    def clear(self):
        self.items = []

    def random_pop(self):
        index = randint(0, len(self.items) - 1)
        return self.ipop(index)

    def stack_pop(self):
        return self.ipop(-1)

    def queue_pop(self):
        return self.ipop(0)

    def middle_pop(self):
        return self.ipop(len(self.items) // 2)

    def __str__(self):
        return "\n".join("{}:\t{}".format(*e) for e in enumerate(self.items))

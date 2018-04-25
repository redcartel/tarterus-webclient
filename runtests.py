from tarterus.maparray import MapArray
from tarterus import passage
from tarterus.engine import Engine, PendingList
from tarterus import room


def engine_tests():
    print("Engine tests:")
    e = Engine({"w": 80, "h": 40, "pop_mode": "queue"})
    assert e.pending.pop == e.pending.queue_pop
    e.step()
    assert isinstance(e.send(["get"])['maparray'], MapArray), str(e)
    assert isinstance(e.send(["get"])['pending'], PendingList), str(e)
    _ = e.send(["add", ["hall", "void", 38, 38, "n", 4, [1, 1]]])
    assert _ == 1, str(e.pending)
    _ = e.send(["add", ["door", "void", 10, 10, "e", 2, [1, 1]]])
    assert _ == 2, str(e.pending)
    _ = e.send(["get"])["pending"][0]
    assert _[0] == "hall", str(_)
    _ = e.pending.pop()
    assert _[0] == "hall", str(_)

# test that pop is random with default construction
# 1 in 2^16 chance that this test fails erroneously
    results = []
    for i in range(16):
        e.send(["set_params", {"w": 40, "h": 20}])
        assert 40 == e.params["w"]
        assert 20 == e.params["h"]
        assert "x" == e.params.get("pop_mode", "x")
        e.send(["clear"])
        assert e.pending.pop != e.pending.queue_pop
        assert e.pending.pop == e.pending.random_pop
        assert 1 == e.send(["add", ["hall", "void", 38, 38, "n", 4, [1, 1]]])
        assert 2 == e.send(["add", ["door", "void", 10, 10, "e", 2, [1, 1]]])
        results.append(e.pending.pop()[0] == "door")
    assert any(x is True for x in results), "random test failed"
    assert not all(x is True for x in results), "random test failed"

    e.send(["set_params", {"w": 80, "h": 40, "pop_mode": "queue"}])
    e.send(['clear'])
    e.add(['hall', 'start', 40, 30, "n", 4, ('hall', 1)])
    e.send(["step_with_command", {"dice": [8, 9]}])
    e.send(["step_with_command", {"dice": [11]}])
    e.send(["step_with_command", {"dice": [17]}])
    e.send(["step_with_command", {"dice": [11]}])
    e.send(["step_with_command", {"dice": [11]}])
    e.send(["step_with_command", {"dice": [11]}])
    e.send(["step_with_command", {"dice": [11]}])

    e.send(['clear'])
    e.add(['hall', 'start', 20, 1, "s", 4, ('hall', 1)])
    e.add(['hall', 'start', 40, 1, "s", 4, ('hall', 2)])
    e.add(['hall', 'start', 60, 1, "s", 4, ('hall', 3)])
    e.add(['hall', 'start', 78, 15, "w", 4, ('hall', 4)])
    e.add(['hall', 'start', 78, 30, "w", 4, ('hall', 5)])
    e.add(['hall', 'start', 40, 38, "n", 4, ('hall', 6)])
    e.add(['hall', 'start', 20, 38, "n", 4, ('hall', 7)])
    e.add(['hall', 'start', 1, 15, "e", 4, ('hall', 8)])
    e.gen_map()
    print(e)


# TODO WRITE TESTS FOR PASSAGE DRAWING w/ COLLISION
def passage_tests():
    print("Tests: ")

    print("turn_across")
    assert (6, 1) == passage.turn_across(1, 1, 'n', 'e', 5)
    assert (0, 1) == passage.turn_across(1, 1, 'n', 'w', 5)
    assert (1, 0) == passage.turn_across(1, 1, 'w', 'n', 5)
    assert (1, 6) == passage.turn_across(1, 1, 'w', 's', 5)
    assert (6, 1) == passage.turn_across(1, 1, 's', 'e', 5)
    assert (0, 1) == passage.turn_across(1, 1, 's', 'w', 5)
    assert (1, 0) == passage.turn_across(1, 1, 'w', 'n', 5)
    assert (1, 6) == passage.turn_across(1, 1, 'w', 's', 5)

    print("draw_passage_section")
    e = Engine({"w": 10, "h": 10, "pop_mode": "queue"})
    # passage.draw_passage_section(m, 8, 1, 'w', 4, 5, ('hall', 1))
    e.step()
    e.add(['hall', 'draw', 8, 1, 'w', (4, 5), ('hall', 1)])
    e.step()
    assert(e.maparray[4, 4] == ('hall', 1))
    # print(e)

    # passage table 1/2
    print("passage_table_1_2")
    e.send(['clear'])
    e.add(['hall', 'start', 4, 1, 's', 2, ('hall', 1)])
    e.send(["step_with_command", {"dice": [2, 7]}])
    assert e.maparray[5, 6] == ('hall', 1), repr(e.maparray[5, 6])
    assert ['hall', 'passage', 4, 7, 's', 2, ('hall', 1)] in e.pending,\
        str(e.pending)

    # passage table 3
    print("passage_table_3")
    e.send(['clear'])
    e.add(['hall', 'start', 1, 8, 'n', 4, ('hall', 1)])
    e.send(["step_with_command", {"dice": [3, 7]}])
    assert e.maparray[4, 3] == ('hall', 1),\
        repr(e.maparray[8, 3])
    assert ['door', 'passage', 5, 4, 'e', 1, ('door', -1)] in e.pending,\
        str(e.pending)
    assert ['hall', 'passage', 1, 2, 'n', 4, ('hall', 1)] in e.pending,\
        str(e.pending)

    # passage table 4
    print("passage_table_4")
    e.send(['clear'])
    e.add(['hall', 'start', 5, 8, 'n', 4, ('hall', 1)])
    e.send(["step_with_command", {"dice": [4, 7]}])
    assert e.maparray[8, 3] == ('hall', 1), repr(e.maparray[8, 3])
    assert ['door', 'passage', 4, 4, 'w', 1, ('door', -1)] in e.pending,\
        str(e.pending)
    assert ['hall', 'passage', 5, 2, 'n', 4, ('hall', 1)] in e.pending,\
        str(e.pending)

    # passage table 5
    e.send(['clear'])
    print("passage_table_5")
    e.add(['hall', 'start', 1, 1, 'e', 6, ('hall', 1)])
    e.send(["step_with_command", {"dice": [5, 7]}])
    assert e.maparray[4, 6] == ("hall", 1)
    assert ['door', 'passage', 5, 4, 'e', 1, ('door', -1)] in e.pending,\
        str(e.pending)

    # passage table 6/7
    e.send(['clear'])
    print("passage_table_6_7")
    e.add(['hall', 'start', 8, 2, 'w', 6, ('hall', 1)])
    e.send(["step_with_command", {"dice": [7, 2]}])
    assert e.maparray[2, 5] == ('hall', 1), repr(e.maparray[2, 5])
    assert e.maparray[1, 5] == ('void', 0), repr(e.maparray[1, 5])
    assert ['hall', 'passage', 4, 1, 'n', 1, ('hall', 1)] in e.pending,\
        str(e.pending)
    assert ['hall', 'passage', 1, 2, 'w', 6, ('hall', 1)] in e.pending,\
        str(e.pending)

    # passage table 8/9
    e.send(['clear'])
    print("passage_table_8_9")
    e.add(['hall', 'start', 8, 2, 'w', 4, ('hall', 1)])
    e.send(['step_with_command', {"dice": [8, 7]}])
    assert e.maparray[2, 5] == ('hall', 1), repr(e.maparray[2, 5])
    assert e.maparray[0, 5] == ('void', 0), repr(e.maparray[1, 4])
    assert ['hall', 'passage', 4, 6, 's', 2, ('hall', 1)] in e.pending,\
        str(e.pending)
    assert ['hall', 'passage', 0, 2, 'w', 4, ('hall', 1)] in e.pending,\
        str(e.pending)

    # passage table 10
    e.send(['clear'])
    print("passage_table_10")
    e.add(['hall', 'start', 1, 8, 'n', 8, ('hall', 1)])
    e.send(["step_with_command", {"dice": [10, 11, 9]}])
    assert e.maparray[8, 5] == ('hall', 1), repr(e.maparray[8, 5])
    assert ['door', 'passage_secret', 5, 4, 'n', 1, ('door', -1)]\
        in e.pending, str(e.pending)

    # passage table 11_12
    print("passage_table_11_12")
    e.send(['clear'])
    e.add(['hall', 'start', 1, 5, 'e', 4, ('hall', 1)])
    e.send(['step_with_command', {"dice": [11, 3]}])
    assert ['hall', 'passage', 5, 2, 'n', 4, ('hall', 1)] in e.pending,\
        str(e.pending)

    e.send(['clear'])
    e.add(['hall', 'start', 1, 1, 's', 4, ('hall', 1)])
    e.send(['step_with_command', {"dice": [11, 3]}])
    assert ['hall', 'passage', 7, 5, 'e', 4, ('hall', 1)] in e.pending,\
        str(e.pending)

    e.send(['clear'])
    e.add(['hall', 'start', 8, 1, 'w', 4, ('hall', 1)])
    e.send(['step_with_command', {"dice": [11, 3]}])
    assert ['hall', 'passage', 1, 7, 's', 4, ('hall', 1)] in e.pending,\
        str(e.pending)

    e.send(['clear'])
    e.add(['hall', 'start', 5, 8, 'n', 4, ('hall', 1)])
    e.send(['step_with_command', {"dice": [11, 3]}])
    assert ['hall', 'passage', 2, 1, 'w', 4, ('hall', 1)] in e.pending,\
        str(e.pending)

    # passage table 13_14
    print("passage_table_13_14")
    e.send(['clear'])
    e.add(['hall', 'start', 5, 1, 's', 2, ('hall', 1)])
    e.send(['step_with_command', {"dice": [13, 3]}])
    assert ['hall', 'passage', 2, 5, 'w', 2, ('hall', 1)] in e.pending,\
        str(e.pending)

    e.send(['clear'])
    e.add(['hall', 'start', 8, 5, 'w', 2, ('hall', 1)])
    e.send(['step_with_command', {"dice": [13, 3]}])
    assert ['hall', 'passage', 3, 2, 'n', 2, ('hall', 1)] in e.pending,\
        str(e.pending)


def room_tests():
    print("room.py")
    e = Engine({"w": 80, "h": 40, "pop_mode": "queue"})
    e.step()

    # test draw_room
    m = MapArray(('void', 0), (10, 10))
    m[5, 5] = ('vwal', 1)
    print("draw_room")
    _ = room.draw_room(m, 1, 1, 8, 8, ('room', 1))
    assert _ is True
    assert m[1, 5] == m[8, 7] == ('vwal', 1)
    assert m[1, 1] == m[8, 1] == ('tcor', 1)
    assert m[8, 8] == m[1, 8] == ('bcor', 1)
    assert m[5, 1] == m[2, 8] == ('hwal', 1)
    assert m[2, 2] == m[7, 7] == ('room', 1)
    # attempt to draw room with blocking tile in the way
    m = MapArray(('void', 0), (10, 10))
    m[5, 5] = ('hall', 1)
    _ = room.draw_room(m, 0, 0, 10, 10, 1)
    assert _ is False
    # draw room from dispatch
    room.dispatch_room(e, ["room", "draw", 1, 1, "e", (8, 8), ("room", 1)],
                       [1, 5, 6])
    m = e.maparray
    assert m[1, 5] == m[8, 7] == ('vwal', 1)
    assert m[1, 1] == m[8, 1] == ('tcor', 1)
    assert m[8, 8] == m[1, 8] == ('bcor', 1)
    assert m[5, 1] == m[2, 8] == ('hwal', 1)
    assert m[2, 2] == m[7, 7] == ('room', 1)

    # test find_loc
    print("find_loc")
    m = MapArray(('void', 0), (40, 40))
    x, y = room.find_loc(m, 20, 1, 20, 10, "s", 1, [6, 5])
    assert (x, y) == (10, 1), str((x, y))
    x, y = room.find_loc(m, 20, 10, 20, 10, "n", 1, [6, 5])
    assert (x, y) == (10, 1), str((x, y))
    m[11, 2] = ('hall', 1)
    x, y = room.find_loc(m, 20, 1, 20, 10, "s", 1, [6, 5])
    assert (x, y) == (19, 1), str((x, y))
    m[35, 2] = ('room', 2)
    x, y = room.find_loc(m, 20, 1, 20, 10, "s", 1, [6, 5])
    assert (x, y) == (15, 1), str((x, y))
    m = MapArray(('void', 0), (40, 40))
    m[4, 4] = ("room", 1)
    m[6, 11] = ("hall", 2)
    x, y = room.find_loc(m, 1, 8, 6, 6, "e", 1, [10, 4])
    assert (x, y) == (1, 5), str((x, y))
    m = MapArray(('void', 0), (40, 40))
    x, y = room.find_loc(m, 1, 10, 6, 6, "e", 1, [6, 5])
    assert (x, y) == (1, 7), str((x, y))
    x, y = room.find_loc(m, 10, 1, 6, 6, "s", 4, [6, 5])
    assert (x, y) == (9, 1), str((x, y))
    m = MapArray(('void', 0), (50, 50))
    # 6 + 5 = 11 - 11 = 0 + (8-2)//2 = 3
    # 30, 20 move north by (3-1) = 18
    x, y = room.find_loc(m, 30, 20, 8, 8, "w", 1, [6, 5])
    assert (x, y) == (23, 16), str((x, y))
    x, y = room.find_loc(m, 30, 20, 8, 8, "w", 4, [6, 5])
    assert (x, y) == (23, 19), str((x, y))

    # room tables
    e.send(['clear'])
    e.add(['room', 'door', 10, 10, "n", 1, ('room', 1)])
    e.send(['step_with_command', {"dice": [13, 3]}])
    print(e)

    


if __name__ == "__main__":
    engine_tests()
    passage_tests()
    room_tests()

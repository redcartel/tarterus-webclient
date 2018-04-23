from tarterus.maparray import MapArray
from tarterus import passage
from tarterus.engine import Engine, PendingList


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

def passage_tests():
    print("Tests: ")
    # m = MapArray(('void', 0), (10, 6))
    # r = passage.draw_passage_section(m, 1, 1, 'e', 4, 5, ('hall', 1))
    # print("draw_passage_section 1,1 w:5 l:5 d:e")
    # print(m)
    # print("returns : " + str(r))
    # m = MapArray(('void', 0), (4, 8))
    # r = passage.draw_passage_section(m, 1, 1, 's', 2, 4, ('hall', 1))
    # print("draw_passage_section 1,1 w:2 l:4, d:s")
    # print(m)
    # print("returns : " + str(r))
    # more to do here

    

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
    m = MapArray(('void', 0), (10, 10))
    ms = set()
    passage.draw_passage_section(m, 8, 1, 'w', 4, 5, ('hall', 1))
    # print(m)

    m = MapArray(('void', 0), (10, 10))
    ms = set()
    print("passage_table_5")
    r = passage.passage_table_5(m, ms, 1, 1, 'e', 6, ('hall', 1), 7)
    assert ('door', 'passage', 5, 4, 'e', 1, ('door', 1)) in ms, str(ms)
    passage.dispatch_door(m, ms, ms.pop())
    # print(m)
    m = MapArray(('void', 0), (10, 10))
    ms = set()
    r = passage.passage_table_5(m, ms, 8, 1, 'w', 6, ('hall', 1), 4)
    # print(m)

    # passage table 6/7
    m = MapArray(('void', 0), (10, 10))
    ms = set()
    print("passage_table_6_7(., ., 1, 5, 'e', 2, ('hall', 1), 7)")
    r = passage.passage_table_6_7(m, ms, 1,5,'e',2,('hall', 1), 7)
    assert r == None
    assert ('hall', 'passage', 7, 5, 'e', 2, ('hall', 1)) in ms, str(ms)
    assert ('hall', 'passage', 4, 7, 's', 2, ('hall', 1)) in ms, str(ms)
    
    # passage table 8/9
    m = MapArray(('void', 0), (10, 10))
    ms = set()
    print("passage_table_8_9(., ., 1, 5, 'e', 2, ('hall', 1), 7)")
    r = passage.passage_table_8_9(m, ms, 1,5,'e',2,('hall', 1), 7)
    assert r == None
    assert ('hall', 'passage', 7, 5, 'e', 2, ('hall', 1)) in ms, str(ms)
    assert ('hall', 'passage', 4, 4, 'n', 2, ('hall', 1)) in ms, str(ms)

    # passage table 10
    m = MapArray(('void', 0), (10, 10))
    ms = set()
    print("passage_table_10()")
    r = passage.passage_table_10(m, ms, 1, 1, 'e',4,('hall', 1), 20)
    assert ('door', 'passage', 5, 2, 'e', 1, ('door', 1)) in ms, str(ms)

    # passage table 11_12
    print("passage_table_11_12")
    m = MapArray(('void', 0), (10, 10))
    ms = set()
    r = passage.passage_table_11_12(m, ms, 1, 5, 'e', 4, ('hall', 1))
    assert ('hall', 'passage', 5, 2, 'n', 4, ('hall', 1)) in ms, str(ms)
    m = MapArray(('void', 0), (10, 10))
    ms = set()
    r = passage.passage_table_11_12(m, ms, 1, 1, 's', 4, ('hall', 1))
    assert ('hall', 'passage', 7, 5, 'e', 4, ('hall', 1)) in ms, str(ms)
    m = MapArray(('void', 0), (10, 10))
    ms = set()
    r = passage.passage_table_11_12(m, ms, 8, 1, 'w', 4, ('hall', 1))
    # print(m)
    assert ('hall', 'passage', 1, 7, 's', 4, ('hall', 1)) in ms, str(ms)
    m = MapArray(('void', 0), (10, 10))
    ms = set()
    r = passage.passage_table_11_12(m, ms, 5, 8, 'n', 4, ('hall', 1))
    # print(m)
    assert ('hall', 'passage', 2, 1, 'w', 4, ('hall', 1)) in ms, str(ms)

    # passage table 13_14 
    print("passage_table_13_14")
    m = MapArray(('void', 0), (10, 10))
    ms = set()
    r = passage.passage_table_13_14(m, ms, 5, 1, 's', 2, ('hall', 1))
    assert ('hall', 'passage', 2, 5, 'w', 2, ('hall', 1)) in ms, str(ms)
    m = MapArray(('void', 0), (10, 10))
    ms = set()
    r = passage.passage_table_13_14(m, ms, 8, 5, 'w', 2, ('hall', 1))
    # print(m)
    assert ('hall', 'passage', 3, 2, 'n', 2, ('hall', 1)) in ms, str(ms)

if __name__ == "__main__":
    engine_tests()
    passage_tests()

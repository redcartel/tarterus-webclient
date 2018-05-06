from tarterus.engine import Engine
from tarterus.level import Level

if __name__ == "__main__":
    e = Engine({"w": 1500, "h": 1500, "pop_mode": "random", "log": True})
    e.add(['start', {'origin': 'm'}])
    e.step()
#     e.add(["hall", "start", 37, 37, "n", 2, ('hall', 1)])
#     e.add(["hall", "start", 39, 38, "e", 2, ('hall', 1)])
#     e.add(["hall", "start", 37, 40, "s", 2, ('hall', 1)])
#     e.add(["hall", "start", 36, 38, "w", 2, ('hall', 1)]) 
    e.gen_map()
    # with open("tmp/output.o", "w") as f:
    #     log = "\n".join(str(r) for r in e.log_messages)
    #     f.write(log)
    #     f.write(str(e))
    #     e.write_choice_log("tmp/output.json")
    lv = Level()
    lv.setmap(e.maparray)
    lv.setdict(e.descriptions)
    lv.write("tmp/bigfile.map")
    print("ok")

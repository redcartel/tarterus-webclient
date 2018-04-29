from tarterus.engine import Engine

e = Engine({"w": 80, "h": 80, "log": True, "pop_mode": "script", "script_file": "tmp/test.json"})
e.init_halls()
e.step()
e.gen_map()
with open("tmp/output.o", "w") as f:
    log = "\n".join(str(r) for r in e.log_messages)
    f.write(log)
    f.write(str(e))
    e.write_choice_log("tmp/output.json")
print("ok")

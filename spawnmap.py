from tarterus.engine import Engine
from tarterus.level import Level
import sys
import os

if __name__ == "__main__":
    id = sys.argv[1]
    w = int(sys.argv[2])
    h = int(sys.argv[3])
    e = int(sys.argv[4])
    os.system("mkdir static/{}".format(id))
    statusfile = "static/{}/{}.update".format(id, id)
    mapfile = "static/{}/{}.map".format(id, id)
    jsonfile = "static/{}/{}.json".format(id, id)
    
    with open(statusfile, 'w') as f:
        f.write('0')
        
    e = Engine({"w": w, "h": h, "pop_mode": "random"})
    e.add(['start', {'origin': e}])
    e.gen_map_files(mapfile, jsonfile, statusfile)

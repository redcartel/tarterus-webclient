from tarterus.engine import Engine
from tarterus.level import Level
import sys
import os

if __name__ == "__main__":
    id = sys.argv[1]
    w = int(sys.argv[2])
    h = int(sys.argv[3])
    e = sys.argv[4]
    os.system("/bin/mkdir static/tmp/{}".format(id))
    statusfile = "static/tmp/{}/{}.update".format(id, id)
    mapfile = "static/tmp/{}/{}.map".format(id, id)
    jsonfile = "static/tmp/{}/{}.json".format(id, id)
    
    with open(statusfile, 'w') as f:
        f.write('0')
        
    e = Engine({"w": w, "h": h, "pop_mode": "random"})
    e.add(['start', {'origin': e}])
    e.gen_map_files(mapfile, jsonfile, statusfile)

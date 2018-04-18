from tarterus.maparray import MapArray  # , MapSquare
from random import randint
import json


LOG = ""

def get_log():
    global LOG
    return LOG


def clear_log():
    global LOG
    LOG = ""


def add_log(txt):
    global LOG
    LOG = LOG + "\n" + txt


def pop_section(maparray, mapset):
    section = mapset.pop()
    if section[0] == 'room':
        add_room(maparray, section, mapset)
    elif section[0] == 'hall':
        add_hall(maparray, section, mapset)


# TODO ROOM NUMBERS
# TODO CHECK ROOM INTERSECTION
def add_room(maparray, section, mapset):
    w = randint(1, 4) * 4 + 2
    h = randint(1, 4) * 4 + 2
    x = 0
    y = 0
    doors = [False, False, False, False]
    for i in range(len(doors)):
        if randint(1, 3) == 2:
            doors[i] = True
    if section[1] == 'n':
        doors[2] = False
        y = section[2] - h + 1
        x = section[3] - w // 4 + randint(0, w // 2)
#    elif section[1] == 'e':
#        x = section[2]
#        y = section[3] - h // 4 + randint(0, h // 2)
#        doors[3] = False
#    elif section[1] == 's':
#        y = section[2]
#        x = section[3] - w // 4 + randint(0, w // 2)
#        doors[0] = False
#    elif section[1] == 'w':
#        x = section[2] - w + 1
#        y = section[3] - h // 4 + randint(0, h // 2)
#        doors[1] = False
    maparray[x:x+w, y:y+h] = room(w, h, 0)
    maparray[section[2], section[3]] = ('door', 0)
#    if doors[0] == True and y > 16:
#        dx = x + w // 4 + randint(0, w // 2)
#        maparray[dx, y] = ('door', 0)
#        mapset.add(('hall', 'n', dx, y - 1))
#    if doors[1] == True and x + w + 16 < maparray.w:
#        dy = y + h // 4 + randint(0, h // 2)
#        maparray[x + w - 1, dy] = ('door', 0)
#        mapset.add(('hall', 'e', x + w, dy))
#    if doors[2] == True and y + h + 16 < maparray.h:
#        dx = x + w // 4 + randint(0, w // 2)
#        maparray[dx, y + h - 1] = ('door', 0)
#        mapset.add(('hall', 's', dx, y + h))
#    if doors[3] == True and x > 16:
#        dy = y + h // 4 + randint(0, h // 2)
#        maparray[x, dy] = ('door', 0)
#        mapset.add(('hall', 'w', x - 1, dy))


def add_hall(maparray, section, mapset):
    l = randint(4,16)
    if section[1] == 'n':
        maparray[section[2],section[3]-l+1:section[3]+1] = ('hall', 0)
        r = 1 # randint(1,8)
        if r == 7 and section[2] + 16 < maparray.w:
            mapset.add(('hall', 'e', section[2] + 1,
                randint(section[3] - 3 * l // 4, section[3] - l // 4)))
        elif r == 8 and section[2] > 16:
            mapset.add(('hall', 'w', section[2] - 1,
                randint(section[3] - 3 * l // 4, section[3] - l // 4)))
        if section[3] - l - 16 > 0:
            mapset.add(('room', 'n', section[2], section[3] - l))
#    if section[1] == 'e':
#        maparray[section[2]:section[2]+l,section[3]] = ('hall', 0)
#        r = randint(1,8)
#        if r == 7 and section[3] + 16 < maparray.h:
#            mapset.add(('hall', 's',
#                randint(section[2] + l // 4, section[2] + 3 * l // 4),
#                section[3] + l))
#        elif r == 8 and section[3] > 16:
#            mapset.add(('hall', 'n',
#                    randint(section[2] + l // 4, section[2] + 3 * l // 4),
#                    section[3]))
#        if section[2] + l + 16 < maparray.w:
#            mapset.add(('room', 'e', section[2]+l-1, section[3]))
#    if section[1] == 's':
#        maparray[section[2], section[3]:section[3]+l] = ('hall', 0)
#        r = randint(1, 8)
#        if r == 7 and section[2] + 16 < maparray.w:
#            :mapset.add(('hall', 'e', section[2] + 1,
#                randint(section[3] + l // 4, section[3] + 3 * l // 4)))
#        elif r == 8 and section[2] > 16:
#            mapset.add(('hall', 'w', section[2] - 1,
#                randint(section[3] + l // 4, section[3] + 3 * l // 4)))
#        if section[3] + l + 16 < maparray.h:
#            mapset.add(('room', 's', section[2], section[3]+l))
#    if section[1] == 'w':
#        maparray[section[2]-l+1:section[2]+1,section[3]] = ('hall', 0)
#        r = randint(1,8)
#        if r == 7 and section[3] + 16 < maparray.h:
#            mapset.add(('hall', 's',
#                randint(section[2] - 3 * l // 4, section[2] - l // 4),
#                section[3] + 1))
#        elif r == 8 and section[3] > 16:
#            mapset.add(('hall', 'n', 
#                randint(section[2] - 3 * l // 4, section[2] - l // 4), 
#                section[3] - 1))
#        if section[2] - l - 16 > 0:
#            mapset.add(('room', 'w', section[2]-l, section[3]))




def room(w, h, rnum):
    mp = MapArray(('room', rnum), (w, h))
    mp[0:w:w-1, 1:h-1] = ('vwal', rnum)
    mp[1:w-1, 0:h:h-1] = ('hwal', rnum)
    mp[0:w:w-1, 0] = ('tcor', rnum)
    mp[0:w:w-1, h-1] = ('bcor', rnum)
    return mp


def gen_map(w, h, typ="default"):
    maparray = MapArray(('void', 0), (w, h))
    x = maparray.w // 2
    y = maparray.h - 1
    mapset = set()
    add_hall(maparray, ('hall', 'n', x, y), mapset)
    while len(mapset) > 0:
        pop_section(maparray, mapset)
    return (maparray, [{}])

def big_room(w, h):
    ma = MapArray(('void', 0), (w, h))
    rlist = [{}]
    x = 3
    y = 3
    rw = w - 6
    rh = h - 6
    ma[x:x+rw, y:y+rh] = room(rw, rh, 1)
    rlist.append({"description": "BIG ROOM DADDY-O"})
    return ma, rlist


def gen_splash(w, h):
    ma = MapArray(('void', 0), (w, h))
    topW = ma.w // 4 * 2
    botW = ma.w // 7
    topH = ma.h // 9
    botH = ma.h // 9 * 5
    topX = ma.w // 4
    botX = ma.w // 7 * 3
    dorX = ma.w // 2 - 1
    topY = ma.h // 9 * 2
    botY = ma.h // 9 * 3 - 1
    topR = room(topW, topH, 1)
    botR = room(botW, botH, 1)
    ma[topX:topX+topW, topY:topY+topH] = topR
    ma[botX:botX+botW, botY:botY+botH] = botR
    ma[dorX, botY] = ('door', 1)
    rlist = [{}]
    rlist.append({"description": """<h2>Tarterus</h2>
    <p>&copy; Carter Adams 2018</p>"""})
    return ma, rlist


def add_feature(ma, rlist, features):
    f = features.pop()
    rn = len(rlist)
    if f['type'] == 'passage':
        ln = randint(4, 10)
        x = f['x']
        y = f['y']
        d = f['d']
        for _ in range(ln):
            ma[x, y] = ('hall', rn)
            if d == 'e':
                x = x + 1
            elif d == 'w':
                x = x - 1
            elif d == 'n':
                y = y - 1
            elif d == 's':
                y = y + 1


def hall_test(w, h):
    ma = MapArray(('void', 0), (w, h))
    rlist = [{}]
    features = set({'type': 'passage', 'x': 1, 'y':  h // 2, 'd': 'e'})
    while len(features) > 0:
        add_feature(ma, rlist, features)
    return ma, rlist


def gen_hall(x, y, d, ma, rn):
    ma[x:x+10, y] = ('hall', rn)


def label_to_n(label):
    TILETABLE = {
        'void': 0,
        'vwal': 1,
        'hwal': 2,
        'room': 3,
        'hall': 4,
        'tcor': 5,
        'bcor': 6,
        'door': 7,
        'sdwn': 8,
        'stup': 9,
        'eror': 10
    }
    try:
        return TILETABLE[label]
    except(KeyError):
        return 9


def maparray_to_json(ma, rlist, log):
    mp = []
    mnums = []
    add_log("end log.")
    for c in range(ma.w):
        mp.append([])
        mnums.append([])
        for r in range(ma.h):
            mp[c].append(label_to_n(ma[c, r][0]))
            mnums[c].append(ma[c, r][1])
    return {
        "mp": mp,
        "rnums": mnums,
        "rlist": rlist,
        "log": log
    }


def fetch_map(w, h, typ="default"):
    maparray = None
    roomlist = None
    clear_log()
    if typ == "default":
        maparray, roomlist = gen_map(w, h)
    if typ == "splash":
        maparray, roomlist = gen_splash(w, h)
    if typ == "big_room":
        maparray, roomlist = gen_splash(w, h)
    if typ == "hall_test":
        maparray, roomlist = gen_map(w, h)
    add_log("fetch_map")
    log = get_log()
    return json.dumps(maparray_to_json(maparray, roomlist, log))


if __name__ == "__main__":
    print("run tests or some shit")

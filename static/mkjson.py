import json
from random import randint

mp = [[0 for r in range(1000)] for c in range(1000)];
rnums = [[0 for r in range(1000)] for c in range(1000)];
rlist = []

def draw_room(x, y, w, h, rnum):
    global mp
    global rnums
    for r in range(y, y+h):
        for c in range(x, x+w):
            rnums[c][r] = rnum
# top corners
            if r == y and (c == x or c == x+w-1):
                mp[c][r] = 5
# bottom corners
            elif r == y+h-1 and (c == x or c == x+w-1):
                mp[c][r] = 6
# side walls
            elif c == x or c == x+w-1:
                mp[c][r] = 1
            elif r == y or r == y+h-1:
                mp[c][r] = 2
            else:
                mp[c][r] = 3

def make_mp():
    rnum = 0
    for r in range(0, 1000, 20):
        for c in range(0, 1000, 40):
            x = c + randint(1,9)
            w = randint(10, 30)
            y = r + randint(1,5)
            h = randint(5, 10)
            rnum += 1
            draw_room(x, y, w, h, rnum)
            rlist.append({
                "x" : x,
                "y" : y,
                "w" : w,
                "h" : h,
                "description" : "ROOM {rnum} at position {x}. {y}. {w} tiles\
wide and {h} tiles high.".format(rnum=rnum, x=x, y=y, w=w, h=h)
                })


def write_file(filename="mp.json"):
    data = {
        "mp" : mp,
        "rnums" : rnums,
        "rlist" : rlist
        }
    with open(filename, "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    make_mp()
    write_file()

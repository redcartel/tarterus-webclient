from tarterus.maparray import MapArray  # , MapSquare
# from random import randint
import json

# D: 0 = north, 1 = east, 2 = south, 3 = west

# class Room:
#     def __init__(self, x, y, d):
#         self.x = x
#         self.y = y
#         self.d = d
#         self.set = false
#
# class Hall:
#     def __init__(self, x, y, d):
#         self.x = x
#         self.y = y
#         self.d = d
#
# def genMap(w,h):
#     roomSet = []
#     hallSet = []
#     rnum = 1
#     hnum = 1
# #     hallSet.add(0, h//2, 1)
# #     while len(hallList) + len(roomList) > 0:
# 
# 
# # mp = [[0 for r in range(1000)] for c in range(1000)]
# # rnums = [[0 for r in range(1000)] for c in range(1000)]
# # rnum = 1
# # rlist = []
# 
# 
# def draw_room(x, y, w, h):
#     global mp
#     global rnums
#     global rnum
#     global rlist
#     for r in range(y, y+h):
#         for c in range(x, x+w):
#             rnums[c][r] = rnum
# # top corners
#             if r == y and (c == x or c == x+w-1):
#                 mp[c][r] = 5
# # bottom corners
#             elif r == y+h-1 and (c == x or c == x+w-1):
#                 mp[c][r] = 6
# # side walls
#             elif c == x or c == x+w-1:
#                 mp[c][r] = 1
#             elif r == y or r == y+h-1:
#                 mp[c][r] = 2
#             else:
#                 mp[c][r] = 3


def room(w, h, rnum):
    mp = MapArray(('room', rnum), (w, h))
    mp[0:w:w-1, 1:h-1] = ('vwal', rnum)
    mp[1:w-1, 0:h:h-1] = ('hwal', rnum)
    mp[0:w:w-1, 0] = ('tcor', rnum)
    mp[0:w:w-1, h-1] = ('bcor', rnum)
    return mp


def gen_map(w, h):
    ma = MapArray(('void', 0), (w, h))
    rlist = [{}]
    ma[w//2: w//2+20, h//2: h//2+20] = room(20, 20, 1)
    rlist.append({"description": "ROOM 1 ROOM 1"})
    return ma, rlist


def label_to_n(label):
    TILETABLE = {
        'void': 0,
        'vwal': 1,
        'hwal': 2,
        'room': 3,
        'hall': 4,
        'tcor': 5,
        'bcor': 6,
        'sdwn': 7,
        'stup': 8,
        'errr': 9
    }
    try:
        return TILETABLE[label]
    except(KeyError):
        return 9


def maparray_to_json(ma, rlist):
    mp = []
    mnums = []
    for c in range(ma.w):
        mp.append([])
        mnums.append([])
        for r in range(ma.h):
            mp[c].append(label_to_n(ma[c, r][0]))
            mnums[c].append(ma[c, r][1])
    return {
        "mp": mp,
        "rnums": mnums,
        "rlist": rlist
    }


def fetch_map(w, h):
    return json.dumps(maparray_to_json(*gen_map(w, h)))


if __name__ == "__main__":
    print("run tests or some shit")

from flask import Flask, render_template, request, send_file
# import json
from tarterus.mapgen import fetch_map  # , gen_splash
from tarterus.engine import Engine
import json
from random import getrandbits
import subprocess

app = Flask("__name__")


@app.route("/randmap/<w>/<h>")
def randmap(w,h):
    return "{} {}".format(w,h)
    # return render_template('index.html')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_bin_map")
def bin_map():
    w = request.args.get('w', '128');
    w = int(w)
    h = request.args.get('h', '128');
    h = int(h)
    e = request.args.get('e', 'm');
    e = str(e)[0]
    idnum = "%032x" % getrandbits(128);
    subprocess.Popen(["python3", "spawnmap.py", 
                      idnum, str(w), str(h), str(3)]);
    return(json.dumps({'id': idnum}))
    



@app.route("/b")
def b():
    return render_template("bintest.html")

@app.route("/big_room")
def big_room():
    w = request.args.get('w', '128')
    w = int(w)
    h = request.args.get('h', '128')
    h = int(h)
    return fetch_map(w, h, "big_room")


@app.route("/default_room")
def default_room():
    w = request.args.get('w', '128')
    w = int(w)
    h = request.args.get('h', '128')
    h = int(h)
    return fetch_map(w, h, "splash")


@app.route("/get_map")
def get_map():
    w = request.args.get('w', '128')
    w = int(w)
    h = request.args.get('h', '128')
    h = int(h)
    t = request.args.get('t', 'splash')
    t = str(t)
    e = request.args.get('e', 's')
    e = str(e)
    l = request.args.get('l', 1)
    l = int(l)
    return fetch_map(w, h, t)


@app.route("/dmg5_map")
def dmg_map():
    w = request.args.get('w', '128')
    w = int(w)
    h = request.args.get('h', '128')
    h = int(h)
    e = request.args.get('e', 's')
    e = str(e)
    l = request.args.get('l', 1)
    l = int(l)
    return fetch_map(w, h, "default", {'entrance': e, 'level': l})

@app.route("/bytes")
def bytes_map():
    w = request.args.get('w', '128')
    w = int(w)
    h = request.args.get('h', '128')
    h = int(h)
    bites = fetch_map(w, h, "binary_test")
    return send_file(
                     bites, 
                     attachment_filename="mapdata.oct",
                     mimetype="application/octet-stream"
                     )

@app.route("/jsontest")
def test():
    return fetch_map(256, 256)
#     ma = maparray.MapArray(('void',0),(1000,1000))
#     ma[450:550,450:550] = ('room',1)
#     ma[425:525,499:501] = ('vwal',1)
#     return jsonout(ma, [{'description' : "THE VOID"}, {'description': "BIG HONKIN ROOM"}])
# 
# def jsonout(maparray, roomlist):
#     global TILETABLE
#     mp = []
#     rnums = []
#     for c in range(len(maparray[0])):
#         mp.append([])
#         rnums.append([])
#         for r in range(len(maparray)):
#             square = maparray[c,r]
#             tilenum = TILETABLE[square[0]]
#             mp[c].append(tilenum)
#             rnums[c].append(square[1])
#     return json.dumps({
#             "mp" : mp,
#             "rnums" : rnums,
#             "rlist" : roomlist
#         })


if __name__ == "__main__":
    app.run("127.0.0.1", 5000, debug=True)

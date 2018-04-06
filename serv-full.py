from flask import Flask, render_template
import json
from tarterus import maparray
app = Flask("__name__")

@app.route("/randmap/<w>/<h>")
def randmap(w,h):
    return "{} {}".format(w,h)
    # return render_template('index.html')

TILETABLE = {
        'void': 0,
        'vwal': 1,
        'hwal': 2,
        'room': 3,
        'hall': 4,
        'tcor': 5,
        'bcor': 6,
        'sdwn': 7,
        'stup': 8
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/jsontest")
def test():
    ma = maparray.MapArray(('void',0),(1000,1000))
    ma[450:550,450:550] = ('room',1)
    ma[425:525,499:501] = ('vwal',1)
    return jsonout(ma, [{'description' : "THE VOID"}, {'description': "BIG HONKIN ROOM"}])

def jsonout(maparray, roomlist):
    global TILETABLE
    mp = []
    rnums = []
    for c in range(len(maparray[0])):
        mp.append([])
        rnums.append([])
        for r in range(len(maparray)):
            square = maparray[c,r]
            tilenum = TILETABLE[square[0]]
            mp[c].append(tilenum)
            rnums[c].append(square[1])
    return json.dumps({
            "mp" : mp,
            "rnums" : rnums,
            "rlist" : roomlist
        })

if __name__ == "__main__":
    app.run("127.0.0.1", 5000, debug=True)

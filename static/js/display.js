var ctx;
var xoffset = 0;
var yoffset = 0;
var tiles = null;
var tileImg = {
    void : [464, 320],
    vwal : [480, 320],
    hwal : [496, 320],
    room : [128, 336],
    hall : [144, 336],
    tcor : [512, 320],
    bcor : [560, 320]
};

var tileNum = [tileImg.void, tileImg.vwal, tileImg.hwal, tileImg.room, tileImg.hall, tileImg.tcor, tileImg.bcor];

var map = null;
var roomlist = [];

function drawRoom(x, y, w, h) {
        for (var c = x; c < x + w; c++) {
                for (var r = y; r < y + h; r++) {
                        map[c][r] = 3;
                }
        }
        for (var c = x; c < x + w; c++) {
                map[c][y] = 2;
                map[c][y+h] = 2;
        }
        for (var r = y; r < y + h; r++) {
                map[x][r] = 1;
                map[x+w][r] = 1;
        }
        map[x][y] = 5;
        map[x+w][y] = 5;
        map[x][y+h] = 6;
        map[x+w][y+h] = 6;
}

function makeMap() {
    map = [];
    for (var i = 0; i < 1000; i++) {
        map[i] = [];
        for (var j = 0; j < 1000; j++) {
            map[i][j] = Math.floor(Math.random() * 5);
        }
    }
    rnum = 0
    for (var i = 0; i < 1000; i += 40) {
        for (var j = 0; j < 1000; j += 20) {
                x = i + Math.floor(Math.random() * 9 + 1);
                w = Math.floor(Math.random() * 20 + 10);
                y = j + Math.floor(Math.random() * 4 + 1);
                h = Math.floor(Math.random() * 5 + 5);
                drawRoom(x, y, w, h);
                roomlist[rnum] = {
                        x: x,
                        y: y,
                        w: w,
                        h: h,
                        description: "Room " + rnum + " located at " + x + ", " + y + "Fusce sed mi vitae velit pharetra vulputate. Pellentesque lectus elit, vehicula ac gravida vitae, tempus nec nibh. Duis placerat magna quis quam ultrices commodo. Vivamus vehicula porta orci ac interdum. Vestibulum laoreet orci arcu, interdum ultrices velit rhoncus ut. Donec mollis arcu ac est bibendum, nec gravida sapien pulvinar. Mauris ut nulla eget erat posuere consequat. Suspendisse lacinia euismod maximus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Duis et faucibus leo."
                }
                rnum++;
        }
    }
    console.log(roomlist[20]);
}

function drawTile(x, y, tile) {
    ctx.drawImage(tiles, tile[0], tile[1], 16, 16, x + xoffset, y + yoffset, 16, 16)
}

$(document).ready(function() {
    console.log('display.js loaded');
    ctx = document.getElementById('display').getContext('2d');
    ctx.canvas.width = window.innerWidth;
    ctx.canvas.height = window.innerHeight;
    tiles = new Image();
    var loaded = false;
    $(tiles).on('load', function() {
        draw();
    });
    tiles.src = 'static/resources/Vanilla_tiles.png';
    makeMap();
});

$(ctx).click(function(e) {
        var x = Math.floor((e.pageX-$("#display").offset().left));
        var y = Math.floor((e.pageY-$("#display").offset().top));
        console.log("click x: " + x + " y: " + y);
        square = getsquare(x, y);
        c = square.c;
        r = square.r;
        console.log("click c: " + c + " r: " + r);
        map[c + 500 + xoffset][r + 500 + yoffset] = 0;
        draw();
});

function getsquare(x, y) {
        c = Math.floor(x / 16);
        r = Math.floor(y / 16);
        return {
                c: c,
                r: r
        }
}

$(window).on('resize', function() {
    ctx.canvas.width = window.innerWidth;
    ctx.canvas.height = window.innerHeight;
    draw();
});

function draw() {
    ctx.clearRect(-1,-1,Math.ceil(ctx.canvas.width) + 1, Math.ceil(ctx.canvas.width) + 1)
    for (var i = -1; i < 1 + Math.ceil(ctx.canvas.width / 16); i++) {
        for (var j = -1; j < 1 + Math.ceil(ctx.canvas.height / 16); j++) {
            drawTile(i*16, j*16, tileNum[map[i + 500 + xoffset][j + 500 + yoffset]]);
        }
    }
}

$(window).keypress(function(event) {
    if (event.which == 104) {
        xoffset -= 1;
        draw()
    }
    else if (event.which == 108) {
        xoffset += 1;
        draw()
    }
    else if (event.which == 106) {
        yoffset += 1;
        draw()
    }
    else if (event.which == 107) {
        yoffset -= 1;
        draw()
    }
});

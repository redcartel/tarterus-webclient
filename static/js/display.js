var ctx;
var xoffset = 0;
var yoffset = 0;
var tiles = null;
var tileImg = {
    void : [464, 320],
    vwal : [480, 320],
    hwal : [496, 320],
    room : [128, 336],
    hall : [144, 336]
};

var tileNum = [tileImg.void, tileImg.vwal, tileImg.hwal, tileImg.room, tileImg.hall];

var map = null;

function makeMap() {
    map = [];
    for (var i = 0; i < 1000; i++) {
        map[i] = [];
        for (var j = 0; j < 1000; j++) {
            map[i][j] = Math.floor(Math.random() * 5);
        }
    }
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

$(window).on('resize', function() {
    ctx.canvas.width = window.innerWidth;
    ctx.canvas.height = window.innerHeight;
    draw();
});

/*
function draw() {
    cols = Math.ceil(ctx.canvas.width / 100);
    console.log("cols: " + cols);
    rows = Math.ceil(ctx.canvas.height / 100);
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    for (var i = 0; i < cols; i++) {
        for (var j = 0; j < rows; j++) {
            var color = 'gray';
            if (i % 2 == 1 && j % 2 == 1) {
                color = 'black';
            }
            else {
                color = 'gray';
            }
            ctx.fillStyle = color;
            ctx.fillRect(i * 100 + xoffset, j * 100 + yoffset, 100, 100);
        }
    }
    drawTile(50,50, tileImg.vwal);
    drawTile(100,100, tileImg.hall);
}
*/

function draw() {
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

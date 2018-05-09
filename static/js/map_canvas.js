/*jshint esversion: 6*/

// XHR doesn't seem to work in a jquery wrapper:
var tartarusDownloadMapBytes = function(id, callback) {
    console.log("getMapBinary");

    var oReq = new XMLHttpRequest();
    oReq.open("GET", "/static/tmp/" + id + "/" + id + ".map", true);
    oReq.responseType = "arraybuffer";
    oReq.onload = function(oEvent) {
        console.log("gMB loaded");
        var arrayBuffer = oReq.response;
        callback(new Uint8Array(arrayBuffer));
    };
    oReq.send();
};

(function() {
    "use strict";
    var tile_offset = 432;
	var globals = {
        loaded: false,
        canvas: null,
	    ctx: null,
	    map: null,
	    section_map: null,
	    room_list: null,
	    tiles: null,
        dragging: false,
        drag_start_x: null,
        drag_start_y: null,
        drag_start_xoffset: null,
        drag_start_yoffset: null,
        selected_room: 0,
        to_draw: false,
        tiles_src: "static/resources/tilemap.png",
	    tileImg: [
		    [464, 320], // void
		    [480, 320], // vwal
		    [496, 320], // hwal
		    [128, 336], // room
		    [144, 336 + tile_offset], // hall
		    [512, 320], // tcor
		    [560, 320], // bcor
		    [64,  336], // door
		    [192, 336], // sdwn
		    [176, 336], // stup
            [0,0], // err
            [16, 336 + tile_offset] // open
        ],
	    highlightTileImg: [
		    [464, 320], // void
		    [480, 320 + 2 * tile_offset], // vwal
		    [496, 320 + 2 * tile_offset], // hwal
		    [128, 336 + 2 * tile_offset], // room
		    [144, 336 + 2 * tile_offset], // hall
		    [512, 320 + 2 * tile_offset], // tcor
		    [560, 320 + 2 * tile_offset], // bcor
		    [64,  336 + 2 * tile_offset], // door
		    [192, 336 + 2 * tile_offset], // sdwn
		    [176, 336 + 2 * tile_offset], // stup
            [0,0], // err
            [16, 336 + 2 * tile_offset] // open
        ],


	};

    var dims = {
        cw: null,
        ch: null,
        mw: null,
        mh: null,
        xoffset: null,
        yoffset: null
    };

    var size_canvas = function(xoff = -1, yoff = -1) {
        globals.canvas.width = window.innerWidth - $(".option-box").width();
        globals.canvas.height = window.innerHeight - $(".header").height();
        globals.canvas.style.left = 0;
        globals.canvas.style.top = $(".header").height();
        globals.ctx.width = window.innerWidth - $(".option-box").width();
        globals.ctx.height = window.innerHeight - $(".header").height();
        dims.cw = Math.ceil(globals.ctx.width / 16);
        dims.ch = Math.ceil(globals.ctx.height / 16);
        if (dims.mw !== null) {
        }
        if (xoff === -1 && dims.mw !== null) {
            dims.xoffset = Math.floor(dims.mw / 2 - dims.cw / 2);
            dims.yoffset = Math.floor(dims.mh / 2 - dims.ch / 2);
        }
        else if (dims.mw !== null) {
            var center_x = Math.floor(xoff + dims.cw / 2);
            var center_y = Math.floor(yoff + dims.ch / 2);
            dims.xoffset = Math.floor(center_x - dims.cw / 2);
            dims.yoffset = Math.floor(center_y - dims.ch / 2);
        }
        if (dims.xoffset !== null) {
        }
    };

    var size_elements = function() {
        $(".flavor-town").height(window.innerHeight - $(".header").height() - $(".option-box").height());
    };

    var drawTile = function(x, y, tile, highlight) {
        if (globals.to_draw) {
            var tileCoords = globals.tileImg[tile];
            if (highlight == true) {
                tileCoords = globals.highlightTileImg[tile];
            }
            globals.ctx.drawImage(globals.tiles, tileCoords[0], tileCoords[1], 16, 16, x*16, y*16, 16, 16);
        }
    };

    var clearCanvas = function() {
        globals.ctx.clearRect(0, 0, $("#display").width(), $("#display").height());
    };

    var draw = function() {
        var x,y;
        var max_x = dims.mw - dims.xoffset;
        var max_y = dims.mh - dims.yoffset;
        for (x = 0; x < dims.cw; x++) {
            for (y = 0; y < dims.ch; y++) {
                if ( (x + dims.xoffset < 0) ||
                     (x + dims.xoffset >= dims.mw) ||
                     (y + dims.yoffset < 0) ||
                     (y + dims.yoffset >= dims.mh) ) {
                    drawTile(x, y, 11);
                }
                else {
                    var rNum = globals.section_map[y + dims.yoffset][x + dims.xoffset];
                    var highlight = false;
                    if (rNum == globals.selected_room) {
                        highlight = true;
                    }
                    drawTile(x, y, globals.map[y + dims.yoffset][x + dims.xoffset], highlight);
                }
            }
        }
    };


    var describe = function(x, y) {
        if (x < 0 || x >= dims.mw || y < 0 || y >= dims.mh) {
            return;
        }
            var number = globals.section_map[y][x];
            globals.selected_room = number;
            console.log(globals.room_list[number]);
            var htmlContent = globals.room_list[number].description;
            htmlContent = htmlContent;
            $("#description").html(htmlContent);
            draw();
        // }
    };

    var genMap = function(w, h, e="m", level=5) {
        globals.to_draw = false;
        clearCanvas();
        var tries = 0;
        var getMapLoadUpdate = function(id) {
            var request = new XMLHttpRequest();
            var updateUrl = "/static/tmp/" + id + "/" + id + ".update";
                $.ajax({
                    'async': true,
                    'global': false,
                    'url': updateUrl,
                    'datatype': 'text',
                    'cache': false,
                    'success': function(data) {
                        if (data != "") {
                            $("#status").html(data);
                        }
                        if(data == 'done') {
                            getMapBinary(id);
                            getMapJson(id);
                        }
                        else {
                            setTimeout(function() {
                                getMapLoadUpdate(id);
                            }, 500);
                        }
                    },
                    'error': function(data, errorStatus, errorThrown) {
                        console.log(errorThrown + " : " + errorStatus);
                        tries += 1;
                        if (tries < 10) {
                            setTimeout(function() {
                                getMapLoadUpdate(id);
                            });
                        }
                    }
                });
                /*
                $("description").html(responseText);
                if (response == "done") {
                    getMapBinary(id);
                    getMapJson(id);
                }
                else {
                    getMapLoadUpdate(id);
                }
                */
            };

        globals.gotBinary = false;
        globals.gotJson = false;
        
        var mapUrl = '/get_bin_map?w=' + w + '&h=' + h + '&e=' + e;
        $.ajax({
            'async': true,
            'global': false,
            'url': mapUrl,
            'dataType': 'json',
            'success': function(data) {
                console.log(data);
                var id = data.id;
                getMapLoadUpdate(id);
            }
        });
    };

    var getMapBinary = function(id) {
        console.log("getMapBinary");
        tartarusDownloadMapBytes(id, function(data) {
            globals.mapByteArray = data;
            globals.gotBinary = true;
            loadNewMap();
        });
    };

    var getMapJson = function(id) {
        console.log("getMapJson");
        $.ajax({
            'async': true,
            'global': false,
            'url': "/static/tmp/"+id+"/"+id+".json",
            'dataType': 'json',
            'success': function(data) {
                console.log("gMJ success");
                globals.mapDictionary = data;
                globals.gotJson = true;
                loadNewMap();
            }
        });
    };

    var loadNewMap = function() {
        if (globals.gotJson == true && globals.gotBinary == true) {
            globals.mapSquares = [];
            globals.roomNumbers = [];
            var w = globals.mapDictionary.w;
            var h = globals.mapDictionary.h;
            var x, y;
            for (y = 0; y < h; y++) {
                globals.mapSquares.push([]);
                globals.roomNumbers.push([]);
                for (x = 0; x < w; x++) {
                    var pos = (y * w * 4) + (x * 4);
                    globals.mapSquares[y].push(globals.mapByteArray[pos]);
                    var b3 = globals.mapByteArray[pos+1];
                    var b2 = globals.mapByteArray[pos+2];
                    var b1 = globals.mapByteArray[pos+3];
                    globals.roomNumbers[y].push(b1 + b2 * 256 + b3 * 256 * 256);
                }
            }
            globals.map = globals.mapSquares;
            globals.section_map = globals.roomNumbers;
            globals.room_list = globals.mapDictionary.descriptions;
            dims.mw = w;
            dims.mh = h;
            size_canvas();
            globals.to_draw = true;
            draw();
        }
    };

    // TODO: refactor this
    $(document).ready(function() {
        globals.canvas = document.getElementById('display');
        globals.ctx = globals.canvas.getContext('2d');
        size_elements();
        size_canvas();
        globals.tiles = new Image();
        var tile_d = $.Deferred();
        var map_d = $.Deferred();
        globals.tiles.src = globals.tiles_src;
        $(globals.tiles).on('load', function() {
            tile_d.resolve();
        });
        genMap(100, 100, "m", 5);
        registerMouseEvents();
        /*var mapUrl = '/default_room?w=' + dims.cw + '&h=' + dims.ch;
        $.ajax({
            'async': true,
            'global': false,
            'url': mapUrl, 
            'dataType': 'json',
            'success': function(data) {
                globals.map = data.mp;
                globals.section_map = data.rnums;
                globals.room_list = data.rlist;
                map_d.resolve();
            },
            'error': function() {
                console.error('! - could not load json map data'); 
            }
        });
        $.when(tile_d, map_d).done(function() {
            if (globals.map === null) {
                console.error('Map not loaded from json');
            }
            else {
                dims.mw = globals.map.length;
                dims.mh = globals.map[0].length;
                size_canvas(-1, -1);
                globals.loaded = true;
                draw();
            }
            registerMouseEvents();
        });
        */
    });

    var registerMouseEvents = function() {

        $('div').click(function(e) {
            globals.dragging = false;
        });

        $('.click-capture').mousedown(function(e) {
            globals.dragging = false;
        });


        // TODO: clean this up
        $("#generate").click(function(e) {
            var re = /\d+/g;
            var val = $("#size").val();
            var w = val.match(re)[0];
            var h = val.match(re)[1];
            genMap(w,h,'m',5);
        });

        $("canvas").click(function(e) {
            globals.dragging = false;
            var xp = Math.floor(e.pageX - $("#display").offset().left);
            var yp = Math.floor(e.pageY - $("#display").offset().top);
            var x = Math.floor(xp / 16);
            var y = Math.floor(yp / 16);
            describe(x + dims.xoffset, y + dims.yoffset);
        });


        $("canvas").mousedown(function(e) {
            globals.drag_start_x = e.pageX;
            globals.drag_start_y = e.pageY;
            globals.drag_start_xoffset = dims.xoffset;
            globals.drag_start_yoffset = dims.yoffset;
            globals.dragging = true;
        });

        $(window).resize(function(e) {
            size_elements();
            size_canvas();
            draw();
        });

        $(document).mouseup(function(e) {
            globals.dragging = false;
        });

        $(document).mousemove(function(e) {
            if (globals.dragging) {
                var dx = globals.drag_start_x - e.pageX;
                var dy = globals.drag_start_y - e.pageY;
                dims.xoffset = globals.drag_start_xoffset + Math.floor(dx / 16);
                dims.yoffset = globals.drag_start_yoffset + Math.floor(dy / 16);
                if (dims.xoffset <= -1 * dims.cw / 2) {
                    dims.xoffset = Math.floor(-1 * dims.cw / 2);
                }
                if (dims.yoffset <= -1 * dims.ch / 2) {
                    dims.yoffset = Math.floor(-1 * dims.ch / 2);
                }
                if (dims.xoffset >= dims.mw - dims.cw / 2) {
                    dims.xoffset = Math.floor(dims.mw - dims.cw /2);
                }
                if (dims.yoffset >= dims.mh - dims.ch / 2) {
                    dims.yoffset = Math.floor(dims.mh - dims.ch / 2);
                }
                draw();
            }
        });


        // TODO: arrow keys wtf?
        $(window).keypress(function(event) {
            if (globals.loaded) {
                if (event.which === 104 || event.which === 37) {
                    if (dims.xoffset > -1 * dims.cw / 2) {
                        dims.xoffset--;
                        draw();
                    }
                }
                if (event.which === 108 || event.which === 39) {
                    if (dims.xoffset < dims.mw - dims.cw / 2) {
                        dims.xoffset++;
                        draw();
                    }
                }
                if (event.which === 107 || event.which === 40) {
                    if (dims.yoffset > -1 * dims.ch / 2) {
                        dims.yoffset--;
                        draw();
                    }
                }
                if (event.which === 106 || event.which === 38) {
                    if (dims.yoffset < dims.mh - dims.ch / 2) {
                        dims.yoffset++;
                        draw();
                    }
                }
            }
        });

    };

})();

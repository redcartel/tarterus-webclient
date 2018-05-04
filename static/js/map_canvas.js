/*jshint esversion: 6*/
//TODO: order functions in a sane way
//


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
        tiles_src: "static/resources/tilemap.png",
	    tileImg: {
		    'void' : [464, 320],
		    'vwal' : [480, 320],
		    'hwal' : [496, 320],
		    'room' : [128, 336],
		    'hall' : [144, 336 + tile_offset],
		    'tcor' : [512, 320],
		    'bcor' : [560, 320],
		    'door' : [64,  336],
		    'sdwn' : [192, 336],
		    'stup' : [176, 336],
            'errr' : [0,0],
            'open' : [16, 336 + tile_offset]
	    },
        tileNum: ['void', 'vwal', 'hwal', 'room', 'hall', 'tcor', 'bcor', 'door', 'sdown', 'stup',  'errr', 'open']
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

    var drawTile = function(x, y, tile) {
        var tileCoords = globals.tileImg[globals.tileNum[tile]];
        globals.ctx.drawImage(globals.tiles, tileCoords[0], tileCoords[1], 16, 16, x*16, y*16, 16, 16);
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
                    drawTile(x, y, globals.map[x + dims.xoffset][y + dims.yoffset]);
                }
            }
        }
    };


    var describe = function(x, y) {
        if (x < 0 || x >= dims.mw || y < 0 || y >= dims.mh) {
            return;
        }
            var number = globals.section_map[x][y];
            console.log(globals.room_list[number]);
            var htmlContent = globals.room_list[number].description;
            htmlContent = "<li class='roomNumber'>" + number + "</li>" + htmlContent;
            $("#description").html(htmlContent);
        // }
    };


    var genMap = function(w, h, typ, ent="s", level=1) {
        var mapUrl = '/get_map?w=' + w + '&h=' + h + '&t=' + typ + '&e=' + ent + '&l=' + level;
        $.ajax({
            'async': true,
            'global': false,
            'url': mapUrl, 
            'dataType': 'json',
            'success': function(data) {
                globals.map = data.mp;
                globals.section_map = data.rnums;
                globals.room_list = data.rlist;
                dims.mw = globals.map.length;
                dims.mh = globals.map[0].length;
                size_canvas();
                draw();
            },
            'error': function() {
                console.error('! - could not load json map data'); 
            }
        });
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
        var mapUrl = '/default_room?w=' + dims.cw + '&h=' + dims.ch;
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
            var tval = $("#type").val();
            genMap(w,h,tval);
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

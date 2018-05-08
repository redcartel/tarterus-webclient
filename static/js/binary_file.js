console.log("initiating");

var oReq = new XMLHttpRequest();
oReq.open("GET", "/bytes", true);
oReq.responseType = "arraybuffer";
oReq.onload = function(oEvent) {
  var arrayBuffer = oReq.response;

  // if you want to access the bytes:
  var byteArray = new Uint8Array(arrayBuffer);
  // ...
  process_map_bytes(byteArray, 128, 128);
};

var squares = [];
var rnums   = [];
var process_map_bytes = function(byteArray, w, h) {
    for (y = 0; y < h; y++) {
        squares.push([]);
        rnums.push([]);
        for (x = 0; x < w; x++) {
            pos = (y * w * 4) + (x * 4);
            squares[y].push(byteArray[pos]);
            // big-endian 3 byte integer
            b3 = byteArray[pos+1];
            b2 = byteArray[pos+2];
            b1 = byteArray[pos+3];
            rnum = b1 + 256 * b2 + 256 * 256 * b3;
            rnums[y].push(rnum);
        }
    }
    for (y = 0; y < h; y++) {
        document.write(rnums[y] + "<br>");
    }
    document.write("<hr>");
    for (y = 0; y < h; y++) {
        document.write(squares[y] + "<br>");
    }
};
oReq.send();

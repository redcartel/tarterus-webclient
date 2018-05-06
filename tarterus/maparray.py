import sys
import types

"""
This module implements the core datatypes of Tarterus, the MapSquare and
MapArray as well as MapVector, which should probably not be used outside of
MapArray
"""


# internal function, turns int n into n:n+1
def _n_to_slice(n):
    if isinstance(n, slice):
        return n
    elif n == -1:
        return slice(-1, None)
    else:
        return slice(n, n+1)


# internal function formats tuples or overly nested lists into a 1d list of
# tuples
def _to_nonempty_tuple_vector(lst):
    try:
        if not isinstance(lst, list):
            lst = [lst]
        elif isinstance(lst[0], tuple):
            return lst
        else:
            while isinstance(lst[0], list):
                lst = lst[0]
    except BaseException:
        tb = sys.exec_info()[2]
        raise TypeError("Expected non-empty vector of tuples"
                        ).with_traceback(tb)
    if not isinstance(lst[0], tuple):
        raise TypeError("Expected non-empty vector of tuples"
                        ).with_traceback(tb)
    return lst


# internal function formats tuples, 1d lists of tuples, or 3d+ lists of tuples
# into a 2d list of tuples
def _to_nonempty_tuple_array(lst):
    try:
        if not isinstance(lst, list):
            lst = [[lst]]
        elif not isinstance(lst[0], list):
            lst = [lst]
        elif isinstance(lst[0][0], tuple):
            return lst
        else:
            while isinstance(lst[0][0], list):
                lst = lst[0]
    except BaseException:
        tb = sys.exec_info()[2]
        raise TypeError("Expected non-empty array of tuples"
                        ).with_traceback(tb)
    if not isinstance(lst[0][0], tuple):
        tb = sys.exec_info()[2]
        raise TypeError("Expected non-empty array of tuples"
                        ).with_traceback(tb)
    return lst


def _decode(_bytes):
    sq_type = MapSquare._FROM_NUM[int.from_bytes(_bytes[0:1], 'big')]
    rnum = int.from_bytes(_bytes[1:4], 'big')
    return MapSquare(sq_type, rnum)


class MapSquare(tuple):
    """
    MapSquare extends tuple to typecheck for (string,int) on construction
    and have a __str__ output derived from roguelike games
    """
    def __new__(cls, *args):
        """
        Construct a new MapSquare

        *args   either a single tuple (string,int) or a string and an int
        """
        if isinstance(args[0], bytes):
            return _decode(args[0])

        if isinstance(args[0], MapSquare):
            return args[0]

        tup = args[0]
        if len(args) == 2:
            tup = (args[0], args[1])
        elif len(args) > 2:
            raise RuntimeError(
                "MapSquare constructor takes 1 or 2 arguments.")
        if not isinstance(tup[0], str) or not isinstance(tup[1], int):
            raise TypeError("MapSquare constructor takes a string and an int.")

        return tuple.__new__(cls, tup)

    def __str__(self):
        """
        String output single character representation of map feature
        """
        return self._CHAR_OUT[self[0]]

    def __repr__(self):
        r = tuple.__repr__(self)
        return 'MapSquare%s' % r

    _CHAR_OUT = {
        'void': ' ',
        'room': '.',
        'hall': '#',
        'door': '+',
        'sdor': '*',
        'sdwn': '>',
        'stup': '<',
        'vwal': '|',
        'hwal': '-',
        'tcor': '^',
        'bcor': 'v',
        'errr': 'X',
        'open': '_'
    }

    _TO_NUM = {
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
        'errr': 10,
        'open': 11
    }

    _FROM_NUM = {
        0: 'void',
        1: 'vwal',
        2: 'hwal',
        3: 'room',
        4: 'hall',
        5: 'tcor',
        6: 'bcor',
        7: 'door',
        8: 'sdwn',
        9: 'stup',
        10: 'errr',
        11: 'open'
    }

    def bytes(self):
        global _TO_NUM
        type_code = MapSquare._TO_NUM[(self[0])].to_bytes(1, 'big')
        rnum_code = self[1].to_bytes(3, 'big')
        return type_code + rnum_code


class MapVector:
    """
    MapVector is a 1 dimensional list of MapSquares that preserves width.

    :property w: width of the vector
    """
    def __init__(self, lst, size=0):
        if isinstance(lst, bytes):
            lstlen = len(lst) // 4
            if size == 0:
                size = lstlen
            chunks = []
            for i in range(size):
                pos = (i % lstlen) * 4
                chunks.append(lst[pos:pos+4])
            _bytes = b''.join(chunks)
        else:
            if isinstance(lst, tuple):
                lst = [lst]
            elif isinstance(lst, types.GeneratorType):
                lst = list(lst)

            if size == 0:
                size = len(lst)
            self.ms_list = [MapSquare(lst[i % len(lst)]) for i in range(size)]
            _bytes = b''.join(ms.bytes() for ms in self.ms_list)
        self.w = size
        self.byte_array = bytearray(_bytes)

    def __repr__(self):
        gen = (bytes(self.byte_array[p:p+4]) for p in range(0, self.w*4, 4))
        msreprs = (', '.join(MapSquare(bs).__repr__() for bs in gen))
        return 'MapVector([{}])'.format(msreprs)

    def __getitem__(self, index):
        if isinstance(index, slice):
            _range = range(*index.indices(self.w))
            indices = (i * 4 for i in _range)
            _bytes = (bytes(self.byte_array[i:i+4]) for i in indices)
            return MapVector(_bytes)
        else:
            if index < 0:
                index = self.w + index
            i = index * 4
            _bytes = bytes(self.byte_array[i:i+4])
            return MapSquare(_bytes)

    def __setitem__(self, index, lst):
        mv = MapVector(lst)

        if isinstance(index, slice):
            _range = range(*index.indices(self.w))
            indices = [i * 4 for i in _range]

        else:
            if index < 0:
                index = self.w + index
            indices = [index * 4]

        for i in range(len(indices)):
            j = indices[i]
            k = (i % mv.w) * 4
            self.byte_array[j:j+4] = mv.byte_array[k:k+4]

    def bytes(self):
        return bytes(self.byte_array)

    def squares(self):
        _bytes = (bytes(self.byte_array[i*4:i*4+4]) for i in range(self.w))
        return [MapSquare(b) for b in _bytes]

    def __str__(self):
        return ''.join(str(ms) for ms in self.squares())

    def __len__(self):
        return len(self.byte_array) // 4


class MapArray:
    """
    A 2 dimensional grid of MapSquares. Provides 2 dimensional selectors
    and set operations that preserve the size of the array.

    self.w  the x-dimension (width) of the MapArray
    self.h  the y-dimension (height) of the MapArray
    """

    def __init__(self, array, siz=(0, 0)):
        self.vectors = []
        if isinstance(array, bytearray):
            array = bytes(array)

        if isinstance(array, bytes):
            w = size[0]
            h = size[1]
            
            if w * h * 4 != len(bytes):
                raise ValueError("specified size must match bytes")
            
            for y in h:
                self.vectors.append(MapVector(array[y*w*4:y*w*4+y*w*4]))
        
        elif isinstance(array, tuple):
            w = size[0]
            h = size[1]

            for _ in range(h):
                self.vectors.append(MapVector(array, w))

        else if isinstance(array, list):
            if isinstance(array[0], bytes):
                for bts in array:
                    self.vectors.append(MapVector(bts))
            else:
                if size == (0, 0):
                    h = len(array)
                    w = len(array[0])
                for r in range(h):
                    vectors.append(MapVector(array[r % len(array)], w))

    def __repr__(self):
        return("MapArray({})".format(self.vectors))

    def __str__(self):
        return("\n".join(str(vec) for vec in self.vectors))


#     def __init__(self, arry, siz=(0, 0)):
#         """
#         Construct a new MapArray
# 
#         arry:   List of list of MapSquare-like tuples. Can also accept list
#                 of tuples or just a tuple.
#         size:   number of rows for a 1 dimensional input or (x,y) dimensions
#                 for a 2 dimensional input. Size of new MapArray. Elements of
#                 arry will be repeated or cropped to accomodate this size.
#         """
#         arry = _to_nonempty_tuple_array(arry)
#         if siz == (0, 0):
#             self.h, self.w = len(arry), len(arry[0])
#         elif not isinstance(siz, tuple):
#             self.h, self.w = siz, len(arry[0])
#         else:
#             self.w, self.h = siz
#         if self.h < 1 or self.w < 1:
#             raise RuntimeError("MapArray cannot have 0 width or height")
# 
#         new = [MapVector(arry[i % len(arry)], self.w) for i in range(self.h)]
#         list.__init__(self, new)

    def __str__(self):
        """
        grid of single character representations of MapSquares
        """
        return "\n".join(str(row) for row in self)

    def __repr__(self):
        r = list.__repr__(self)
        return 'MapArray(%s)' % r

    def __getitem__(self, select):
        """
        get square, rows, or subarray with 2d selectors

        select: - If select is a 2-dimensional selector [x,y] returns the
                MapSquare at the given coordinate location.
                - If select is a 2-dimensional selector [a,b] where a or b or
                both are a range, returns a MapArray copy of the given
                subregion of the array
                - If select is a 1 dimensional selector (int or range) then
                __getitem__ behaves as list.__getitem__ and returns reference
                or list of references to constituent MapVectors

                note maparray[y][x] = maparray[x,y]
        """
        if not isinstance(select, tuple):
            return list.__getitem__(self, select)  # MapVector or [MapVectors]

        c, r = select
        if not isinstance(r, slice) and not isinstance(c, slice):
            return list.__getitem__(self, r)[c]  # MapSquare
        else:
            c = _n_to_slice(c)
            r = _n_to_slice(r)
            return MapArray([row[c] for row in list.__getitem__(self, r)])

    def __setitem__(self, select, arry):
        """
        __setitem__     dimension-preserving change to MapArray contents

        select: - If select is a 2-dimensional selector consisting of either
                coordinates or ranges, replaces MapSquares in-place with the
                squares in arry. Cropping or repeating arry as needed to
                preserve dimensions

                - If select is a 1-dimensional selector (row number or range)
                then the selected rows are reference-replaced with copies to
                new rows taken from arry. arry may be widened, contracted, or
                repeated as needed to preserve dimension.

        arry:   A MapArray object with the new squares. A MapVector or
                MapSquare (or similarly structured object) will be accepted as
                well.
        """
        if not isinstance(select, tuple):
            select = _n_to_slice(select)
            ma = MapArray(arry, (self.w, len(self[select])))
            list.__setitem__(self, select, ma)

        else:
            arry = _to_nonempty_tuple_array(arry)
            c, r = select
            c = _n_to_slice(c)
            r = _n_to_slice(r)
            ind = range(len(self))[r]
            for i in range(len(ind)):
                self[ind[i]][c] = arry[i % len(arry)]  # with MapVector []=

    # TODO: MAKE MORE ROBUST WITH RANGE NOTATION
    def squares(self, x=0, y=0, w=0, h=0):
        if (x, y, w, h) == (0, 0, 0, 0):
            w = self.w
            h = self.h
        for r in range(y, y+h):
            for c in range(x, x+w):
                yield self[r][c]

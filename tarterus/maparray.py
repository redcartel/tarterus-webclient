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

    def __init__(self, array, size=(0, 0)):
        self.vectors = []

        # convert bytearray into bytes
        if isinstance(array, bytearray):
            array = bytes(array)

        # get list from generator (need length)
        if isinstance(array, types.GeneratorType):
            array = list(array)

        # make a copy of an existing maparray (possibly at a new size)
        if isinstance(array, MapArray):
            array = array.vectors

        # build a MapArray from a MapVector
        if isinstance(array, MapVector):
            array = [array]

        # build a MapArray from a bytestring
        if isinstance(array, bytes):
            w = size[0]
            h = size[1]

            if w * h * 4 != len(array):
                raise ValueError("specified size must match bytes")

            for y in range(h):
                self.vectors.append(MapVector(array[y*w*4:y*w*4+w*4]))

        # build a MapArray repeating a MapSquare over a w x h space
        elif isinstance(array, tuple):
            w = size[0]
            h = size[1]

            if w == 0 and h == 0:
                w = 1
                h = 1

            for _ in range(h):
                self.vectors.append(MapVector(array, w))

        elif isinstance(array, list):
            # build a MapArray from a list of bytestrings
            if isinstance(array[0], bytes):
                for bts in array:
                    self.vectors.append(MapVector(bts))

            else:
                # force a 2 dimensional array
                if isinstance(array[0], tuple):
                    array = [array]

                if size == (0, 0):
                    h = len(array)
                    w = len(array[0])
                else:
                    w = size[0]
                    h = size[1]

                # if the input does not
                for r in range(h):
                    self.vectors.append(MapVector(array[r % len(array)], w))
        self.w = self.vectors[0].w
        self.h = len(self.vectors)

    def __repr__(self):
        return("MapArray({})".format(self.vectors))

    def __str__(self):
        return("\n".join(str(vec) for vec in self.vectors))

    def __len__(self):
        return len(self.vectors)

    def __getitem__(self, index):
        # if index is not a tuple, return vector(s)
        if not isinstance(index, tuple):
            return self.vectors[index]

        else:
            if isinstance(index[1], slice):
                yi = range(*index[1].indices(len(self.vectors)))

            else:
                # return MapSquare for [int,int] index
                if not isinstance(index[0], slice):
                    return self.vectors[index[1]][index[0]]

                else:
                    yi = [index[1]]
            # return sub-MapArray if either index is a range
            vecs = (MapVector(self.vectors[y][index[0]]) for y in yi)
            return MapArray(vecs)

    def __setitem__(self, index, target):
        # if index is not a tuple, operate like a normal list of MapVectors
        if not isinstance(index, tuple):
            self.vectors[index] = target
        else:

            if isinstance(index[1], slice):
                yi = range(*index[1].indices(len(self.vectors)))
            else:
                yi = [index[1]]

            target = MapArray(target)
            for i in range(len(yi)):
                pos = i % target.h
                self.vectors[yi[i]][index[0]] = target[pos]

    # used mainly for "any" and "all" tests
    def squares(self):
        ret = []
        for vec in self.vectors:
            ret.extend(vec.squares())
        return ret

    def bytes(self):
        return b''.join(vec.bytes() for vec in self.vectors)

    def bytelist(self):
        return [vec.bytes() for vec in self.vectors]

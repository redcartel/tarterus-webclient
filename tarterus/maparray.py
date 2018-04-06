import sys

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
    }


class MapVector(list):
    """
    MapVector is a 1 dimensional list of MapSquares that preserves width.

    :property w: width of the vector
    """
    def __init__(self, lst, siz=0):
        """
        Construct a new MapVector from a list of MapSquare-like objects
        the MapVector is a copy of the list, even if that list is a MapVector
        itself

        list:       list of MapSquares. Must not be empty. If lst is a
                    non-list, it is treated like a 1 element list.

        siz:        the desired length of the constructed vector. The list will
                    be cropped or repeated as needed to achieve this.
        """
        lst = _to_nonempty_tuple_vector(lst)
        if siz == 0:
            siz = len(lst)
        new = [MapSquare(lst[i % len(lst)]) for i in range(siz)]
        list.__init__(self, new)
        self.w = len(self)

    def __str__(self):
        """
        Row of chars from MapSquares.
        """
        return "".join(str(e) for e in self)

    def __repr__(self):
        r = list.__repr__(self)
        return 'MapVector(%s)' % r

#   Decided to leave list __getitem__ as is, which means slices do not return
#   new MapVectors. MapVector should not be used outside of this Module.

    def __setitem__(self, select, lst):
        """
        []= Size-preservinge in-place replacement of MapSquares & slices

        select: index or range of MapSquares to be replaced
        lst:    MapSquare or list of MapSquares from which to replace. Will be
                repeated or cropped to preserve width of the MapVector
        """
        lst = _to_nonempty_tuple_vector(lst)
        select = _n_to_slice(select)
        ind = range(len(self))[select]
        for i in range(len(ind)):
            list.__setitem__(self, ind[i], MapSquare(lst[i % len(lst)]))


class MapArray(list):
    """
    A 2 dimensional grid of MapSquares. Provides 2 dimensional selectors
    and set operations that preserve the size of the array.

    self.w  the x-dimension (width) of the MapArray
    self.h  the y-dimension (height) of the MapArray
    """
    def __init__(self, arry, siz=(0, 0)):
        """
        Construct a new MapArray

        arry:   List of list of MapSquare-like tuples. Can also accept list
                of tuples or just a tuple.
        size:   number of rows for a 1 dimensional input or (x,y) dimensions
                for a 2 dimensional input. Size of new MapArray. Elements of
                arry will be repeated or cropped to accomodate this size.
        """
        arry = _to_nonempty_tuple_array(arry)
        if siz == (0, 0):
            self.h, self.w = len(arry), len(arry[0])
        elif not isinstance(siz, tuple):
            self.h, self.w = siz, len(arry[0])
        else:
            self.w, self.h = siz
        if self.h < 1 or self.w < 1:
            raise RuntimeError("MapArray cannot have 0 width or height")

        new = [MapVector(arry[i % len(arry)], self.w) for i in range(self.h)]
        list.__init__(self, new)

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

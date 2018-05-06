from tarterus.maparray import MapSquare
from tarterus.maparray import MapVector
from tarterus.maparray import MapArray
import unittest


# TODO: make these work if the acii representation of squares change
# (that will suck)

# TODO: tests for empty constructors, getters, setters etc.
# think about graceful results

# TODO: test meaningless or ambiguous inputs
# ask about pythonic way of handling this

# TODO: test for meaningful errors when that shit is written

class MapArrayModuleTest(unittest.TestCase):

    def test01_SqConstruct(self):
        self.assertEqual(MapSquare('hall', 0).__repr__(), "MapSquare('hall', 0)", "Two Arg Constructor")
        self.assertEqual(str(MapSquare('hall', 0)), '#', "Two Arg Constructor")
        self.assertEqual(MapSquare(('room', 0)).__repr__(), "MapSquare('room', 0)", "Constructor with tuple")
        self.assertEqual(str(MapSquare(('room', 0))), '.', "Constructor with tuple")
        self.assertEqual(MapSquare(MapSquare('stup', 0)).__repr__(), "MapSquare('stup', 0)", "Nested constructor")
        self.assertEqual(str(MapSquare(MapSquare('stup', 0))), "<")
        s = MapSquare('hall', 10)
        _ = s.bytes()
        self.assertEqual((4).to_bytes(1, 'big')+(10).to_bytes(3, 'big'), _)
        t = MapSquare(_)
        self.assertEqual(s, t)


    def test02_SqImmutable(self):
        self.assertEqual(isinstance(MapSquare('vwal', 0), tuple), True, "tuple inheritance")
        self.assertEqual(isinstance(MapSquare(('vwal', 0)), tuple), True, "tuple inheritance")
        a = MapSquare('hwal', 0)
        b = MapSquare('hwal', 0)
        self.assertEqual(a, b, "equality by value")

    def test03_VecConstruct(self):
        mv1 = MapVector([MapSquare('door', 0)])
        st1 = "MapVector([MapSquare('door', 0)])"
        self.assertEqual(mv1.__repr__(), st1)
        self.assertEqual(str(mv1), "+")
        mv2 = MapVector(('door', 0))
        self.assertEqual(mv2.__repr__(), st1)
        self.assertEqual(str(mv1), "+")
        mv3 = MapVector([MapSquare('vwal', 1), MapSquare('room', 2), MapSquare('vwal', 3)])
        st2 = "MapVector([MapSquare('vwal', 1), MapSquare('room', 2), MapSquare('vwal', 3)])"
        self.assertEqual(mv3.__repr__(), st2, "MapVector constructor from list of MapSquares")
        self.assertEqual(str(mv3), "|.|", "MapVector constructor from list of MapSquares - str")
        mv4 = MapVector([('vwal', 1), ('room', 2), ('vwal', 3)])
        self.assertEqual(mv4.__repr__(), st2, "MapVector constructor from list of tuples")
        self.assertEqual(str(mv4), "|.|", "MapVector constructor from list of tuples - str")
        mv6 = MapVector([MapSquare('hall', 0) for _ in range(3)])
        st3 = "MapVector([MapSquare('hall', 0), MapSquare('hall', 0), MapSquare('hall', 0)])"
        self.assertEqual(mv6.__repr__(), st3, "MapVector constructor with list comprehension")
        self.assertEqual(str(mv6), "###", "MapVector constructor with list comperhension - str)")
        mv5 = MapVector(mv4)
        self.assertEqual(mv5.__repr__(), st2, "Nested MapVector constructor is copies value")
        self.assertNotEqual(id(mv4), id(mv5), "Nested MapVector constructor does not copy pointer")
        l1 = [("room", 3), ("room", 4), ("room", 5)]
        mv7 = MapVector(l1)
        mv8 = MapVector(l1)
        self.assertNotEqual(id(mv7), id(mv8), "MapVector constructor from same list does not duplicate pointer")
        s1 = MapSquare("void", 0)
        mv9 = MapVector(s1)
        mv10 = MapVector(s1)
        self.assertNotEqual(id(mv9), id(mv10), "MapVector constructor from same MapSquare does not duplicate pointer")
        ma = MapArray([mv4, mv6])
        mv11 = MapVector(ma)
        self.assertEqual(str(mv11), "|.|")

    def test04_VecNConstruct(self):
        mv1 = MapVector(('door',1),3)
        st1 = "MapVector([MapSquare('door', 1), MapSquare('door', 1), MapSquare('door', 1)])"
        self.assertEqual(mv1.__repr__(), st1, "Repeat construction with single element")
        mv2 = MapVector([('door', 1), ('vwal', 2)],6)
        self.assertEqual(str(mv2),"+|+|+|", "Repeat construction with multiple elements")
        mv3 = MapVector(mv2,7)
        self.assertEqual(str(mv3),"+|+|+|+", "Partial repeat constructor with MapVector")
        mv4 = MapVector(mv3,3)
        self.assertEqual(str(mv4),"+|+", "Cut MapVector short")

    def test06_VecGet(self):
        mv1 = MapVector([("void", 0), ("hall", 0), ("door", 0), ("room", 0), ("vwal",0)])
        self.assertEqual(str(mv1), " #+.|", "string of original vector")
        self.assertEqual(str(mv1[1]), "#", "str of [1]")
        self.assertTrue(isinstance(mv1[1], MapSquare), "integer index returns MapSquare")
        #self.assertTrue(isinstance(mv1[0:3], MapVector), "range index returns MapVector")
        #self.assertTrue(isinstance(mv1[3:4], MapVector), "single-element range returns MapVector")
        self.assertEqual(str(mv1[-1]), "|", "str of [-1]")
        #self.assertEqual(str(mv1[1:4]), "#+.", "str of [1:4]")
        #self.assertEqual(str(mv1[0:5:2]), " +|", "str of [0:5:2]")

    def test07_VecSet(self):
        mv1 = MapVector([("void", 0), ("hall", 0), ("door", 0), ("room", 0), ("vwal",0)])
        self.assertEqual(str(mv1), " #+.|", "string of original vector")
        mv1[1] = ("door",0)
        self.assertEqual(str(mv1), " ++.|", "string after [1]={door}")
        id1 = id(mv1)
        mv1[1] = ("hall",0)
        id2 = id(mv1)
        self.assertEqual(id1, id2, "modification in place")
        mv1[1:3] = ("room",0)
        self.assertEqual(str(mv1), " ...|", "string after [1:3]={room}")
        mv1[0:5:2] = ("sdwn",0)
        self.assertEqual(str(mv1), ">.>.>", "string after [0:5:2]={sdwn}")
        # id3 = id(mv1)
        mv2 = MapVector([("stup",0) for _ in range(5)])
        id4 = id(mv2)
        mv1[:] = mv2
        id5 = id(mv1)
        self.assertEqual(str(mv1), str(mv2), "equality after [:] = ")
        self.assertNotEqual(id5, id4, "full copy does not copy pointer")
        self.assertEqual(id5, id1, "all changes have been in-place")
        mv1[1:4] = [('hall', 0), ('room', 0)]
        self.assertEqual(str(mv1), "<#.#<", "set range to MapVector")
        mv2[0:4] = mv1[2:4]
        self.assertEqual(str(mv2), ".#.#<", "set range to range")

    def test08_MapArrayConstructor(self):
        ma1 = MapArray(('hall',10))
        st1 = "MapArray([MapVector([MapSquare('hall', 10)])])"
        self.assertEqual(ma1.__repr__(), st1, "constructor with single MapSquare")
        ma1 = MapArray(('hall',10),1)
        self.assertEqual(ma1.__repr__(), st1, "single-square constructor with 1 dimensional size parameter")
        ma1 = MapArray(('hall',10),(1,1))
        self.assertEqual(ma1.__repr__(), st1, "single-square constructor with 2 dimensional size parameter")
        st2 = "##"
        st2b = "MapArray([MapVector([MapSquare('hall', 0), MapSquare('hall', 0)])])"
        ma2 = MapArray(('hall',0),(2,1))
        self.assertEqual(ma2.__repr__(), st2b, "(2,1) __repr__ test")
        self.assertEqual(str(ma2), st2, "(2,1) size constructor")
        st3 = "#\n#"
        st3b = "MapArray([MapVector([MapSquare('hall', 0)]), MapVector([MapSquare('hall', 0)])])"
        ma3 = MapArray(('hall',0),(1,2))
        self.assertEqual(str(ma3), st3, "(1,2) size constructor")
        self.assertEqual(ma3.__repr__(), st3b, "(1,2) __repr__ test")
        mv1 = MapVector(('room',2), 3)
        ma4 = MapArray(mv1)
        self.assertEqual(str(mv1),str(ma4), "Constructor with single MapVector")
        ma4 = MapArray([('room',2) for i in range(3)])
        self.assertEqual(str(mv1),str(ma4), "Constructor with 1d list")
        ma5 = MapArray(mv1, (2,1))
        st5 = ".."
        self.assertEqual(str(ma5), st5, "Constructor restricts x dimension")
        mv2 = MapVector([('hall', 1), ('door', 1)])
        ma6 = MapArray(mv2, (5,1))
        st6 = "#+#+#"
        self.assertEqual(str(ma6), st6, "Constructor expands x dimension")
        ma7 = MapArray(mv2, 2)
        st7 = "#+\n#+"
        self.assertEqual(str(ma7), st7, "Constructor expands y dimension, single parameter")
        ma1b = MapArray(ma1)
        ma7b = MapArray(ma7)
        self.assertEqual(ma1.__repr__(), ma1b.__repr__(), "Constructor as identity on MapArray 1x1")
        self.assertEqual(ma7.__repr__(), ma7b.__repr__(), "Constructor as identity on MapArray 2x2")
        id1 = id(ma7)
        id2 = id(ma7b)
        self.assertNotEqual(id1, id2, "Constructor copies value not reference")
        mv3 = MapVector([('hwal', 0), ('door', 1)])
        mv4 = MapVector(mv3,3)[1:]
        ma8 = MapArray([mv3,mv4])
        st8 = "-+\n+-"
        self.assertEqual(str(ma8), st8, "Constructor with list of MapVectors")
        mv5 = MapVector(mv4,10)
        ma8 = MapArray([mv3,mv5])
        self.assertEqual(str(ma8), st8, "Constructor with list of irregular MapVectors (keep dimension of top row)")
        ma9 = MapArray(ma8,(3,3))
        st9 = "-+-\n+-+\n-+-"
        self.assertEqual(str(ma9), st9, "Constructor expands Maparray (2x2) -> (3x3)")
        ma10 = MapArray(ma9, (5,1))
        st10 = "-+--+"
        self.assertEqual(str(ma10), st10, "Constructor expands in one dimension and contracts in another (3x3) -> (5,1)")

    def test09_ArrayGet(self):
        mv1 = MapVector([('door', 0), ('hwal', 1)])
        mv2 = MapVector([('hall', 0), ('room', 1)])
        ma1 = MapArray([mv1,mv2], (5,5))
        print('\n' + str(ma1))
        # row getters
        mv3 = ma1[1]
        st3 = "#.#.#"
        self.assertEqual(str(mv3), "#.#.#", "get single row element")
        self.assertTrue(isinstance(mv3, MapVector), "single int parameter is MapVector")
        li1 = ma1[1:5]
        self.assertTrue(type(li1) == list, "single-dimension slice is standard list")
        mv4 = li1[1]
        st4 = "+-+-+"
        self.assertTrue(isinstance(mv4, MapVector), "element of list is MapVector")
        self.assertEqual(str(mv4), st4, "get element from slice of rows")
        ms1 = ma1[1,1]
        self.assertTrue(isinstance(ms1, MapSquare), "[int,int] returns single MapSquare")
        self.assertEqual(str(ms1), ".", "[int,int] correct element")
        # changed MapArray get result types
        #mv5 = ma1[1][1:3]
        #mv6 = ma1[1:3,1]
        # self.assertTrue(isinstance(mv6, MapVector), "[range,y] returns MapVector")
        #self.assertEqual(str(mv5),str(mv6), "[range, y] returns the right MapVector")

        # get single square
        mc = ('hall',0)
        self.assertEqual(ma1[2,1], mc, "get correct single MapSquare from [int,int]")

        # column slice tests
        ma2a = ma1[1,1:2]
        self.assertEqual((1,1),(ma2a.w,ma2a.h),"1x1 column slice")
        ma2 = ma1[1,1:3]
        self.assertEqual((1,2),(ma2.w,ma2.h),"1x2 column slice")
        st2 = ".\n-"
        st2b = "MapArray([MapVector([MapSquare('room', 1)]), MapVector([MapSquare('hwal', 1)])])"
        self.assertEqual(ma2.__repr__(), st2b, "get range on single column __repr__")
        self.assertEqual(len(ma2), 2)
        self.assertEqual(type(ma2[1]), MapVector, "2 MapVector rows")
        self.assertEqual(str(ma2), st2, "get range on single column")

        ma3 = MapArray(ma1, (2,3))
        ma4 = ma1[2:4,2:6]
        self.assertEqual(str(ma3), str(ma4), "slices in multiple dimensions")

        ma5 = ma1[3:5, 4:5]
        st5 = "-+"
        self.assertTrue(isinstance(ma5, MapArray), "1 row slice is still MapArray")
        self.assertEqual(str(ma5), st5, "correct 1 row slice")

    def test10_ArraySet(self):
        mvs = []
        mvs.append(MapVector([('void', 0), ('hall', 0)], 8))
        mvs.append(MapVector([('room', 0), ('sdor', 0)], 8))
        mvs.append(MapVector([('vwal', 0), ('hwal', 0)], 8))
        mvs.append(MapVector([('sdwn', 0), ('stup', 0)], 8))
        ma1 = MapArray(mvs)
        print("\n" + str(ma1))
        st1 = "\n".join([str(mv) for mv in mvs])
        self.assertEqual(str(ma1), st1)
        ma1[2] = mvs[3]
        mvs2 = [mvs[0], mvs[1], mvs[3], mvs[3]]
        st2 = "\n".join([str(mv) for mv in mvs2])
        self.assertEqual(str(ma1), st2, "replace single row")
        ma1[2] = ('door', 0)
        mvd = MapVector(('door', 0), 8)
        mvs3 = [mvs[0], mvs[1], mvd, mvs[3]]
        st3 = "\n".join([str(mv) for mv in mvs3])
        self.assertEqual(str(ma1), st3, "replace row with single square")
        ma1[0:5:2] = mvs[2]
        mvs4 = [mvs[2], mvs[1], mvs[2], mvs[3]]
        st4 = "\n".join([str(mv) for mv in mvs4])
        self.assertEqual(str(ma1), st4, "replace slice with single row")
        ma1 = MapArray(mvs)
        ma1[1:3] = mvs
        mvs5 = [mvs[0], mvs[0], mvs[1], mvs[3]]
        st5 = "\n".join([str(mv) for mv in mvs5])
        self.assertEqual(str(ma1), st5, "replace slice with larger list")

        # set 2d
        ma1 = MapArray(mvs)
        ma1[0,0] = ('door',1)
        st6 = "+#\n.*"
        self.assertEqual(str(ma1[0:2,0:2]), st6, "set single square")
        ma1[1:4,1] = ('door',1)
        st7 = ".+++.*.*"
        self.assertEqual(str(ma1[1]), st7)
        ma2 = MapArray(('room', 0), (4,4))
        st8 = "...."
        st9 = ".++."
        st10 = "\n".join([st8,st9,st9,st8])
        ma2[1:3,1:3] = ('door',1)
        self.assertEqual(str(ma2), st10)
        ma1[1:7,1:3] = ma2
        print(ma1)

if __name__ == '__main__':
    unittest.main()

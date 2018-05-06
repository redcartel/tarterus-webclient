from tarterus.maparray import MapArray
import pickle


class Level():

    def __init__(self):
        self.file_obj = {
            'w': 0,
            'h': 0,
            'dictionary': {},
            'mapbytes': b''
        }

    def setmap(self, marray):
        self.file_obj['mapbytes'] = marray.bytes()
        self.file_obj['w'] = marray.w
        self.file_obj['h'] = marray.h

    def setdict(self, dictionary):
        self.file_obj['dictionary'] = dictionary

    def write(self, filename):
        with open(filename, 'wb') as outfile:
            pickle.dump(self.file_obj, outfile)

    def read(self, filename):
        with open(filename, 'rb') as infile:
            self.file_obj = pickle.load(infile)

    def getdict(self):
        return self.file_obj['dictionary']

    def getlevel(self):
        w = self.file_obj['w']
        h = self.file_obj['h']
        bts = self.file_obj['mapbytes']
        return MapArray(bts, (w, h))

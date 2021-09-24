import json


class ReadData():
    def __init__(self):
        self.file_path = None
        self.meta_path = None
        self.data = None

    def set_json_paths(self, tunes_path = None, meta_path = None):
        if tunes_path is not None:
            self.file_path = tunes_path
        else:
            self.file_path = './dataset/chords.json'
        if meta_path is not None:
            self.meta_path = meta_path
        else:
            self.meta_path = './dataset/meta_info.json'

    def readData(self, modifier):
        """
        Reads the parsed json file and creates a list of dictionnaries. Each list element contains a list of the chords
        of one single tune.
        :param modifier: function pointer to the function who defines how to encode a chord:
                         one of rootAndDegrees(), rootAndDegreesBasic(),  rootAndDegreesOnly7()
        :return:
        """
        self.data = json.load(open(self.file_path))
        self.meta = json.load(open(self.meta_path))

        represent = lambda chord: {'root': chord['root'],
                                   'components': modifier(chord['degrees']),
                                   'bass': chord['bass'],
                                   'measure': chord['measure'],
                                   }
        # store the names of the dictionary keys
        names = list(self.data.keys())

        # store the chord sequences
        seqs = []
        # loop over all tunes
        for key in self.data.keys():
            song = self.data[key]
            seq = []
            for measure_num in song.keys():
                measure = song[measure_num]
                for chord in measure:
                    chord['measure'] = int(measure_num)
                    seq += [represent(chord)]
            seqs += [seq]
        return seqs, names

    # return root, 'm' for minor, '7' for dominant, 'm7' for minor dominant, 'dim' for diminished TODO m7b5?
    def rootAndDegrees(self):
        return self.readData(lambda x: x)

    # return only the root of the chord
    def rootOnly(self):
        def modifier(degrees):
            return []

        return self.readData(modifier)

    # keep only the root and the 'm' for minor chords
    def rootAndDegreesBasic(self):
        def modifier(degrees):
            no7 = degrees[:]
            if 1 in no7: no7.remove(1)
            if 2 in no7: no7.remove(2)
            if 3 not in no7 and 4 not in no7: no7 += [4]
            if 5 in no7: no7.remove(5)
            if 6 in no7: no7.remove(6)
            if 8 in no7: no7.remove(8)
            if 9 in no7: no7.remove(9)
            if 10 in no7: no7.remove(10)
            if 11 in no7: no7.remove(11)
            no7.sort()
            return no7

        return self.readData(modifier)

    # return root, 'm' for minor, '7' for dominant, 'm7' for minor dominant
    def rootAndDegrees7(self):
        def modifier(degrees):
            no7 = degrees[:]
            if 1 in no7: no7.remove(1)
            if 2 in no7: no7.remove(2)
            if 3 not in no7 and 4 not in no7: no7 += [4]
            if 3 in no7 and 4 in no7: no7.remove(3)
            if 5 in no7: no7.remove(5)
            if 6 in no7: no7.remove(6)
            if 8 in no7: no7.remove(8)
            if 9 in no7: no7.remove(9)
            no7.sort()
            return no7

        return self.readData(modifier)


    def rootAndDegreesSimplified(self):
        """
        Reduce 9, 11, 13 chords to 7 chords
        Reduce aug, sus to 7 chords
        Keep 6 chords and m7b5
        Note: (+13) will be kept since it is the same as the 6
        """
        def modifier(degrees):
            no7 = degrees[:]
            if 1 in no7: no7.remove(1)
            if 2 in no7: no7.remove(2)
            if 3 not in no7 and 4 not in no7: no7 += [4]
            if 3 in no7 and 4 in no7: no7.remove(3)
            if 5 in no7: no7.remove(5)
            if 8 in no7: no7.remove(8)
            no7.sort()
            return no7

        return self.readData(modifier)
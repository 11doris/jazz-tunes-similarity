import json


class ReadData():
    def __init__(self):
        self.file_path = './dataset/chords.json'
        self.meta_path = './dataset/meta_info.json'
        self.data = None

    def set_json_paths(self, tunes_path = None, meta_path = None):
        if tunes_path is not None:
            self.file_path = tunes_path
        if meta_path is not None:
            self.meta_path = meta_path

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
        # store the information about which beat the chords are
        beats = []
        # loop over all tunes
        for tune in self.data.keys():
            song = self.data[tune]
            seq = []
            beats_tune = []
            for measure_num in song.keys():
                measure = song[measure_num]
                beats_bar = []
                for beat, chord in measure.items():
                    chord['measure'] = int(measure_num)
                    seq += [represent(chord)]
                    beats_bar += beat
                beats_tune += [beats_bar]
            seqs += [seq]
            beats += [beats_tune]

        return seqs, names, beats

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
            if 11 in no7: no7.remove(11)
            if 3 in no7 and 10 in no7: no7.remove(10)
            no7.sort()
            return no7

        return self.readData(modifier)


    def rootAndDegreesSimplified(self):
        """
        Reduce 9, 11, 13 chords to 7 chords
        Reduce aug, sus to 7 chords
        Keep 6 chords and m7b5
        Keep sus and sus7, reduce sus11 and sus13 to sus7   
        Note: (+13) will be kept since it is the same as the 6

        """
        def modifier(degrees):
            no7 = degrees[:]
            if 1 in no7: no7.remove(1)
            if 2 in no7: no7.remove(2)
            if 3 in no7 and 4 in no7: no7.remove(3)
            if no7 == [7]: no7 += [4] # extend C5 to C
            if 6 in no7 and 7 in no7: no7.remove(6)  # remove #11
            if 8 in no7: no7.remove(8)
            if 9 in no7 and 11 in no7: no7.remove(9) # remove #13
            if 3 in no7 and 5 in no7 and 7 in no7 and 10 in no7: no7.remove(5)  # reduce m11 to m
            if 5 in no7 and 9 in no7: no7.remove(9)
            no7.sort()
            return no7

        return self.readData(modifier)

    def rootAndDegreesPlus(self):
        """
        Reduce 9, 11, 13 chords to 7 chords
        Reduce aug to 7 chords
        Reduce M7, 6 to major triads
        Reduce m7, m6 to minor triads
        Keep m7b5, dim, dim7, sus, sus7
        Note: (+13) will be kept since it is the same as the 6

        """
        def modifier(degrees):
            no7 = degrees[:]
            if 1 in no7: no7.remove(1)
            if 2 in no7: no7.remove(2)
            if 3 in no7 and 4 in no7: no7.remove(3)
            if no7 == [7]: no7 += [4] # extend C5 to C
            if 4 in no7 and 5 in no7: no7.remove(5)
            if 6 in no7 and 7 in no7: no7.remove(6)  # remove #11
            if 6 in no7 and 4 in no7: no7.remove(6)  # remove b5 for major chords
            if 8 in no7: no7.remove(8)
            if 9 in no7 and not 6 in no7: no7.remove(9)  # reduce m6 and 6, leave dim7
            if 9 in no7 and 11 in no7: no7.remove(9) # remove #13
            if 9 in no7 and 6 in no7: no7.remove(9)  # reduce dim7 to dim
            if 11 in no7: no7.remove(11)  # remove M7
            if 3 in no7 and 5 in no7 and 7 in no7 and 10 in no7: no7.remove(5)  # reduce m11 to m
            if 3 in no7 and 7 in no7 and 10 in no7: no7.remove(10) # reduce m7 to m


            no7.sort()
            return no7

        return self.readData(modifier)


import json
import os
import re
from chords.chord import Chord
from dataset.readData import ReadData


class ChordSequence:
    def __init__(self, config=None, meta=None):
        if config is None:
            _config_file = 'config.json'
        else:
            _config_file = config
        # read config file
        self.config = json.load(open(_config_file))

        # read the raw data as a data object
        self.data_obj = ReadData()
        self.data_obj.read_tunes()

    def _simplify_chords(self):
        # use simplified basic chords - or full chords?
        if self.config['config']['use_basic_chords']:
            data, names = self.data_obj.rootAndDegreesSimplified()
        else:
            data, names = self.data_obj.rootAndDegrees()
        return data

    def fill_up_bar(self, _seq, _beats):
        # get max number of chords per bar
        max_chords = max([len(set(i)) for i in _seq])

        # _seq is modified in this function!! create a copy of _seq and return this. Or change the test.

        # fill up the chords to have the same number of chords in each bar
        if max_chords == 1:
            pass
        elif max_chords == 2:
            if _beats == 4:
                for index, measure in enumerate(_seq):
                    if len(measure) == 2:
                        continue
                    _seq[index].append(measure[0])
            elif _beats == 3 or _beats == 6:
                for index, measure in enumerate(_seq):
                    if len(measure) == 1:
                        new_seq = [measure[0]] * 3
                        _seq[index] = new_seq
                    elif len(measure) == 2:
                        new_seq = [measure[0]] * 2
                        new_seq.append(measure[1])
                        _seq[index] = new_seq
            elif _beats == 2:
                for index, measure in enumerate(_seq):
                    if len(measure) == 2:
                        continue
                    _seq[index].append(measure[0])
            else:
                raise NotImplementedError("Unsupported number of beats for 2 chords!")
        elif max_chords == 4 or max_chords == 3:
            if _beats == 4:
                for index, measure in enumerate(_seq):
                    if len(measure) == 4:
                        continue
                    if len(measure) == 1:
                        new_seq = [measure[0]] * 4
                        _seq[index] = new_seq
                    elif len(measure) == 2:
                        new_seq = [measure[0]] * 2
                        new_seq.append(measure[1])
                        new_seq.append(measure[1])
                        _seq[index] = new_seq
                    elif len(measure) == 3:
                        new_seq = [measure[0]] * 2
                        new_seq.append(measure[1])
                        new_seq.append(measure[2])
                        _seq[index] = new_seq
            elif _beats == 3:
                for index, measure in enumerate(_seq):
                    if len(measure) == 3:
                        continue
                    elif len(measure) == 2:
                        new_seq = [measure[0]] * 2
                        new_seq.append(measure[1])
                        _seq[index] = new_seq
                    elif len(measure) == 1:
                        new_seq = [measure[0]] * 3
                        _seq[index] = new_seq
            else:
                raise NotImplementedError(f"Unsupported Beat with max_chords={max_chords}")
        else:
            raise NotImplementedError("Unsupported Max Number of Chords per Measure!")
        return _seq

    def read_data(self):
        # TODO: Move this Code!!
        directory = self.config['config']['output_directory']
        if not os.path.exists(directory):
            os.makedirs(directory)

        subdir = os.path.join(directory, 'chords')
        if not os.path.exists(subdir):
            os.makedirs(subdir)

        data = self._simplify_chords()

        sequences = []
        for i in range(len(data)):
            tune = data[i]
            seq = []
            # initialize the chord sequence with an empty list per measure
            for n in range(tune[len(tune) - 1]['measure']):
                seq.append([])

            # transpose a major tune to C major, and a minor tune to A minor
            #### TODO key = 3 if mode_dict[i] == 'major' else 0
            key = 3
            for chord in tune:
                formatted_chord = Chord(chord).toSymbol(key=key, includeBass=False)
                # delete all the chord extensions (+b9), (+#9), (+b11), (+#11), (+b13), (+#13)
                formatted_chord = re.sub('\(\+[b#]?[0-9]+\)', '', formatted_chord)
                # replace mM9 chord by mM7 because it occurs only once
                formatted_chord = re.sub('mM9$', 'mM7', formatted_chord)
                # replace all maug chords; they occur only once minor-augmented =
                seq[chord['measure'] - 1].append(formatted_chord)
                # print("Bar {}: {}".format(chord['measure'], formatted_chord))

            print(self.data_obj.meta[str(i)]['title'])
            seq = self.fill_up_bar(seq, self.data_obj.meta[str(i)]['beat-time']['beats'])
            sequences += [seq]

        assert (len(self.data_obj.meta) == len(sequences))

        for _id, tune in enumerate(sequences):
            # print(self.data_obj.meta[str(_id)]['title'])
            # print(f'    {sequences[_id]}')
            self.data_obj.meta[str(_id)]['out'] = {}
            self.data_obj.meta[str(_id)]['out']['chords'] = tune
            # self.data_obj.meta[str(_id)]['out']['duration'] = self.data_obj.duration[str(_id)]

        return self.data_obj.meta

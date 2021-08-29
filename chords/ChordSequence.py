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

        if meta is None:
            _meta_file = 'dataset/meta_info.json'
        else:
            _meta_file = meta
        # read meta information
        self.meta = json.load(open(_meta_file))

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

    #def _get_key(self):

    def read_data(self):

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
                seq += [formatted_chord]
                # print("Bar {}: {}".format(chord['measure'], formatted_chord))
            sequences += [seq]

        assert(len(self.meta) == len(sequences))

        for _id, tune in enumerate(sequences):
            print(self.meta[str(_id)]['title'])
            print(f'    {sequences[_id]}')

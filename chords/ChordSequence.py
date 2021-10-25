import json
import os
import re
from chords.chord import Chord
from dataset.readData import ReadData
import pandas as pd

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
        self.data_obj.set_json_paths()

        # define output directory and create if not available
        directory = self.config['config']['output_directory']
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.out_dir = os.path.join(directory, 'chords')
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        self.chord_seq_file = os.path.join(self.out_dir, 'chord_sequences.json')

    def _simplify_chords(self):
        # use simplified basic chords - or full chords?
        if self.config['config']['use_basic_chords']:
            data, names = self.data_obj.rootAndDegreesSimplified()
        else:
            data, names = self.data_obj.rootAndDegrees()
        return data, names

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
            elif _beats == 5:
                for index, measure in enumerate(_seq):
                    if len(measure) == 1:
                        new_seq = [measure[0]] * 2
                        _seq[index] = new_seq
                    elif len(measure) == 2:
                        new_seq = [measure[0]]
                        new_seq.append(measure[1])
                        _seq[index] = new_seq
                    else:
                        raise NotImplementedError('Unsupported number of chords for 5 beats')
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
            elif _beats == 3 or _beats == 5:
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

    def write_sequences(self, out):
        f = open(self.get_chord_sequences_path(), "w")
        f.write(json.dumps(out, indent=None))
        f.close()

    def get_chord_sequences_path(self):
        return self.chord_seq_file

    def create_sequence(self, data, names, mode='relative'):
        sequences = []
        for i in range(len(data)):
            tune = data[i]
            seq = []
            # initialize the chord sequence with an empty list per measure
            for n in range(tune[len(tune) - 1]['measure']):
                seq.append([])

            if mode == 'relative':
                # transpose a major tune to C major, and a minor tune to A minor
                song_key = self.data_obj.meta[names[i]]['default_key']['mode']
                assert song_key in ['minor', 'major']
                key = 3 if song_key == 'major' else 0
            elif mode == 'default':
                # use the default key
                key = self.data_obj.meta[names[i]]['default_key']['key']
            else:
                quit(f'Unknown mode "{mode}" to generate the chord sequence.')

            for chord in tune:
                formatted_chord = Chord(chord).toSymbol(key=key, includeBass=False)

                # delete all the chord extensions (+b9), (+#9), (+b11), (+#11), (+b13), (+#13)
                #formatted_chord = re.sub('\(\+[b#]?[0-9]+\)', '', formatted_chord)
                # replace mM9 chord by mM7 because it occurs only once
                #formatted_chord = re.sub('mM9$', 'mM7', formatted_chord)
                # replace all maug chords; they occur only once minor-augmented =

                seq[chord['measure'] - 1].append(formatted_chord)
                # print("Bar {}: {}".format(chord['measure'], formatted_chord))

            #seq = self.fill_up_bar(seq, self.data_obj.meta[names[i]]['time_signature']['beats'])
            sequences += [seq]
        return sequences

    def create_leadsheet_chords(self):
        data, names = self._simplify_chords()

        sequences_relative = self.create_sequence(data, names, mode='relative')
        sequences_default = self.create_sequence(data, names, mode='default')

        assert (len(self.data_obj.meta) == len(sequences_default))

        data = []
        for i, tune in enumerate(sequences_default):
            # generate a list with the section label for each measure
            section_labels = []
            section_name = None
            start_measure = 1
            for section_start, next_section_name in self.data_obj.meta[names[i]]['sections'].items():
                section_start = int(section_start)
                for n in range(start_measure, len(tune)):
                    if n < section_start:
                        section_labels.append(section_name)
                    else:
                        start_measure = n
                        section_name = next_section_name
                        break
            for n in range(start_measure, len(tune)+1):
                section_labels.append(section_name)

            assert len(tune) == len(section_labels)

            start_of_section = [False] * len(tune)
            for measure, section_name in self.data_obj.meta[names[i]]['sections'].items():
                start_of_section[int(measure)-1] = True

            list_of_tuples = list(zip([names[i]]*len(tune),
                                      list(range(1, len(tune)+1)),
                                      tune,
                                      sequences_relative[i],
                                      section_labels,
                                      start_of_section))
            data.extend(list_of_tuples)

        df = pd.DataFrame(data, columns=['file_name',
                                         'MeasureNum',
                                         'ChordsDefault',
                                         'ChordsRelative',
                                         'SectionLabel',
                                         'StartOfSection'])
        return df




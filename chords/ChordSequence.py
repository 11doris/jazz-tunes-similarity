import json
import os
import re
from chords.chord import Chord
from dataset.readData import ReadData
import pandas as pd
from tqdm import tqdm

class ChordSequence:
    def __init__(self, chord_style='leadsheet', config=None, meta=None):

        if chord_style not in ['leadsheet', 'ascii']:
            raise NotImplementedError(f'Unsupported style to generate chord sequences: {chord_style}')

        self.chord_style = chord_style

        if config is None:
            _config_file = 'config.json'
        else:
            _config_file = config

        # read config file
        self.config = json.load(open(_config_file))

        # read the raw data as a data object
        self.data_obj = ReadData()
        self.data_obj.set_json_paths()

        # TODO output the csv result files to this directory

        # define output directory and create if not available
        directory = self.config['config']['output_directory']
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.out_dir = os.path.join(directory, 'chords')
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)


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
                if self.chord_style == 'leadsheet':
                    formatted_chord = Chord(chord).toHtmlLeadSheet(key=key, includeBass=False)
                else:
                    formatted_chord = Chord(chord).toSymbol(key=key, includeBass=False)

                seq[chord['measure'] - 1].append(formatted_chord)
                # print("Bar {}: {}".format(chord['measure'], formatted_chord))

            sequences += [seq]
        return sequences

    def create_leadsheet_chords(self):
        data, names, beats = self.data_obj.rootAndDegrees()

        sequences_relative = self.create_sequence(data, names, mode='relative')
        sequences_default = self.create_sequence(data, names, mode='default')

        assert len(beats) == len(sequences_relative)
        assert len(beats) == len(sequences_default)
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
                                      beats[i],
                                      section_labels,
                                      start_of_section))
            data.extend(list_of_tuples)

        df = pd.DataFrame(data, columns=['file_name',
                                         'MeasureNum',
                                         'ChordDefault',
                                         'ChordRelative',
                                         'Beat',
                                         'SectionLabel',
                                         'StartOfSection'])

        # explode multiple chords per measure to one chord per row and add the beat count
        df = df.explode(['ChordDefault', 'ChordRelative', 'Beat'])
        df['Beat'] = pd.to_numeric(df['Beat'])

        df['default_Root1'] = [d.get('root1') for d in df['ChordDefault']]
        df['default_Root2'] = [d.get('root2') for d in df['ChordDefault']]
        df['relative_Root1'] = [d.get('root1') for d in df['ChordRelative']]
        df['relative_Root2'] = [d.get('root2') for d in df['ChordRelative']]
        df['chord_down'] = [d.get('down') for d in df['ChordDefault']]
        df['chord_alt_up'] = [d.get('alt-up') for d in df['ChordDefault']]
        df['chord_alt_down'] = [d.get('alt-down') for d in df['ChordDefault']]
        df = df.drop(columns=['ChordDefault', 'ChordRelative'])

        return df


    def split_tunes_in_sections(self, chords='rootAndDegreesPlus'):

        if chords == 'rootAndDegreesPlus':
            data, names, beats = self.data_obj.rootAndDegreesPlus()
            filename = '03b_input_wordembedding_sections_rootAndDegreesPlus.csv'
        else:
            data, names, beats = self.data_obj.rootAndDegreesSimplified()
            filename = '03b_input_wordembedding_sections_simplified.csv'

        seq = self.create_sequence(data, names, mode='relative')

        df = pd.DataFrame(columns=['file_name', 'title', 'title_playlist', 'tune_mode', 'tune_id', 'section_name', 'section_id', 'chords'])

        for i, tune in tqdm(enumerate(seq)):
            meta = self.data_obj.meta[names[i]]
            meta_row = [meta['file_path'], meta['title'], meta['title_playlist'], meta['default_key']['mode']]

            # generate a list with the chords for each section
            sections = self.data_obj.meta[names[i]]['sections']
            tune_name = self.data_obj.meta[names[i]]['title']
            #print(f"{tune_name}")
            if len(sections) > 0:
                section_bar_num = [int(num) for num in sections.keys()]
                section_names = list(sections.values())
                idx = 0
                first_section = True
                section_chords = []
                for measure, chords in enumerate(tune, start=1):
                    #print(f'{measure}: {", ".join(chords)}')

                    if idx < len(section_bar_num):
                        if measure == section_bar_num[idx]:
                            if first_section:
                                first_section = False
                                row = meta_row[:]
                            else:
                                #print(f'Section {section_names[idx-1]}, {", ".join(section_chords)}')
                                row.extend([i, section_names[idx-1], idx, " ".join(section_chords)])
                                df.loc[len(df)] = row
                                section_chords = []
                                row = meta_row[:]
                            idx += 1
                    section_chords.extend(chords)
                #print(f'Last Section {section_names[-1]}, {" ".join(section_chords)}')
                row.extend([i, section_names[-1], idx, " ".join(section_chords)])
                df.loc[len(df)] = row
                row = meta_row[:]
            else:
                flatten_chords = [chord for bar in tune for chord in bar]
                #print(f'No Sections. {" ".join(flatten_chords)}')
                row = meta_row[:]
                row.extend([i, None, 0, " ".join(flatten_chords)])
                df.loc[len(df)] = row

        # save result to csv file
        df.to_csv(filename, sep='\t', encoding='utf-8', index=True, index_label="id")
        print(f'Wrote dataframe to {filename}.')

        return df


    # TODO this is probably not used; repeated chords are removed in the colab file.
    def remove_repeated_chords(self, seq):
        out = []
        for tune in seq:
            last_chord = None
            tune_norep = []
            flattened_chords = [chord for bar in tune for chord in bar]
            for chord in flattened_chords:
                if chord != last_chord:
                    tune_norep.append(chord)
                    last_chord = chord
            out.append(tune_norep)
        return out


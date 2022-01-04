from model.config import input_files, get_test_tunes, preprocess_config
import pandas as pd
import logging
import os


def _remove_chord_repetitions(chords):
    previous = ''
    chords_norep = []
    for c in chords:
        if c != previous:
            chords_norep.append(c)
            previous = c
    return chords_norep


def _make_ngrams(tokens, n=2, sep='-'):
    return [sep.join(ngram) for ngram in zip(*[tokens[i:] for i in range(n)])]


def _get_list_of_test_tunes():
    test_tunes = []
    for ref, sim in get_test_tunes():
        if ref not in test_tunes:
            test_tunes.append(ref)
        if sim not in test_tunes:
            test_tunes.append(sim)
    test_tunes.sort()
    return test_tunes


class PrepareData:
    def __init__(self, chords_preprocessing='rootAndDegreesPlus'):
        """
        Reads the input data and stores it into dataframes:
        self.df: read from the csv. dataframe with full information; one per section and tune, same sections per tune
                 are retained. Includes the metadata with title, tune mode etc.
        self.df_section: if multiple sections with the same label for a tune, keep only the first section.

        Provides helper functions to translate between title and sectionid, and rowid

        :param chords_preprocessing:
        """
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

        self.chords_preprocessing = chords_preprocessing
        self.ngrams = preprocess_config['ngrams']
        self.remove_repetitions = preprocess_config['remove_repetitions']

        self.input_file = input_files[chords_preprocessing]

        self.df = pd.read_csv(self.input_file, sep='\t', index_col="id")
        self.df['title_section'] = self.df['title_playlist'] + ', ' + self.df['section_name']
        self.df = self.df.reset_index()

        # if multiple sections with same label, reduce dataset to just one
        self.df_section = (self.df
                               .sort_values(['tune_id', 'section_name', 'section_id'])
                               .drop_duplicates(['tune_id', 'section_name'], keep='first')
                               .loc[:, ['id', 'chords', 'title_playlist', 'section_name']]
                               )
        self.df_section.rename(columns={'id': 'sectionid'}, inplace=True)
        self.df_section['chords'] = self.df_section['chords'].str.split(' ')
        self.df_section.reset_index(inplace=True, drop=True)

        ##
        # Helper functions to translate between titles and sections
        titles = self.df.loc[:, ['id', 'tune_id', 'section_id', 'section_name', 'title', 'title_playlist']]
        self._titles_dict = titles.to_dict()

        tunes = self.df.loc[:, ['tune_id', 'title_playlist']].drop_duplicates()
        self.tunes = tunes.set_index('tune_id').to_dict()
        titles_rows = titles.to_dict(orient='records')

        # given the sectionid, provide a string with the title and the section label
        self._sectionid_to_section = []
        for i, row in enumerate(titles_rows):
            name = f"{row['title']}, section{row['section_id']} ({row['section_name']})"
            self._sectionid_to_section.append(name)

        # given the sectionid, return the name of the section, e.g. 'A', 'B', 'C'...
        self._sectionid_to_sectionlabel = []
        for i, row in enumerate(titles_rows):
            self._sectionid_to_sectionlabel.append(row['section_name'])

        # given the title, provide a list of all corresponding sectionids (including duplicate sections)
        self._title_to_sectionid = {}
        for row in titles.iterrows():
            title = row[1]['title_playlist']
            if title not in self._title_to_sectionid:
                self._title_to_sectionid[title] = [row[1]['id']]
            else:
                self._title_to_sectionid[title].append(row[1]['id'])

        # list with the sectionid of the sections considered for training (omitting duplicate sections per tune)
        self._title_to_sectionid_unique_section = {}
        for row in self.df_section.iterrows():
            title = row[1]['title_playlist']
            if title not in self._title_to_sectionid_unique_section:
                self._title_to_sectionid_unique_section[title] = [row[1]['sectionid']]
            else:
                self._title_to_sectionid_unique_section[title].append(row[1]['sectionid'])

        # prepare a list of all sectionids under test
        self.test_tune_sectionid = []
        for title in _get_list_of_test_tunes():
            self.test_tune_sectionid.extend(self.title_to_sectionid_unique_section(title))

        # make sure that the directories for storing output files exist
        if not os.path.exists('output'):
            os.makedirs('output')
        if not os.path.exists('output/model'):
            os.makedirs('output/model')

        # load the Corpus
        self.__corpus()

        ###
    # public helper functions
    def sectionid_to_title(self, id):
        return self._titles_dict['title_playlist'][id]

    def sectionid_to_titleid(self, id):
        return self._titles_dict['tune_id'][id]

    def titleid_to_title(self, id):
        return self.tunes['title_playlist'][id]

    def title_to_titleid(self, id):
        titleid_dict = {v: k for k, v in self.tunes['title_playlist'].items()}
        return titleid_dict[id]

    def sectionid_to_section(self, id):
        return self._sectionid_to_section[id]

    def sectionid_to_sectionlabel(self, id):
        return self._sectionid_to_sectionlabel[id]

    def title_to_sectionid(self, id):
        return self._title_to_sectionid[id]

    def title_to_sectionid_unique_section(self, title):
        return self._title_to_sectionid_unique_section[title]

    ###
    # Corpus processing

    # depending on the configuration, remove subsequent identical chords or add ngrams of the chords.
    def preprocess_input(self, chord_list):
        tune_n = []
        if self.remove_repetitions:
            chord_list = _remove_chord_repetitions(chord_list)
        for n in self.ngrams:
            tune_n.extend(_make_ngrams(chord_list, n=n))
        return tune_n

    # process the input data, which is the unique sections of the tunes
    def __corpus(self):
        self.df_test = pd.DataFrame(columns=['sectionid', 'chords'])
        self.df_train = pd.DataFrame(columns=['sectionid', 'chords'])

        test_corpus_chords = []
        train_corpus_chords = []

        test_sectionid = []
        train_sectionid = []

        # for each unique section of a tune, process the chords
        for id, line in self.df_section.iterrows():
            sectionid = line['sectionid']
            tune_n = self.preprocess_input(line['chords'])

            # to the train_corpus, add only the sections which are not used by the contrafacts tests
            if sectionid in self.test_tune_sectionid:
                test_corpus_chords.append(tune_n)
                test_sectionid.append(sectionid)
            else:
                train_corpus_chords.append(tune_n)
                train_sectionid.append(sectionid)

        self.df_test = pd.DataFrame(list(zip(test_sectionid, test_corpus_chords)),
                                    columns=['sectionid', 'chords'])
        self.df_test.set_index('sectionid', inplace=True)

        self.df_train = pd.DataFrame(list(zip(train_sectionid, train_corpus_chords)),
                                     columns=['sectionid', 'chords'])
        self.df_train.set_index('sectionid', inplace=True)

        self.df_train_test = pd.concat([self.df_train, self.df_test]).reset_index().reset_index().set_index('sectionid')

        print(f'Train Corpus: {len(self.df_train)}')
        print(f'Test Corpus: {len(self.df_test)}')

    def get_test_corpus(self):
        return self.df_test

    def get_train_corpus(self):
        return self.df_train

    def get_train_test_sectionid(self, id):
        return self.df_train_test.iloc[id].name

    def get_train_test_meta(self):

        meta = pd.read_csv(f'output/preprocessing/02c_tune_sql_import.csv', sep='\t')
        meta = meta[['id', 'title_playlist', 'year_truncated', 'tune_mode']].drop_duplicates()
        assert (len(meta) == len(self.df.loc[:, ['tune_id']].drop_duplicates()))

        _df = pd.DataFrame()
        _df['sectionid'] = self.df_train_test.index.to_list()
        _df = (self.df.loc[:,['title_playlist', 'title_section', 'tune_id']]
               .merge(_df, left_index=True, right_on='sectionid')
               )
        _df = _df.sort_index()
        _df = (_df
               .merge(meta, left_on='tune_id', right_on='id'))
        return _df

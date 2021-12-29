from model.config import input_files, get_test_tunes
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
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

        self.chords_preprocessing = chords_preprocessing
        self.ngrams = [1,2]
        self.remove_repetitions = False

        self.input_file = input_files[chords_preprocessing]

        df = pd.read_csv(self.input_file, sep='\t', index_col="id")
        df = df.reset_index()
        self.df = df

        titles = df.loc[:, ['id', 'tune_id', 'section_id', 'section_name', 'title', 'title_playlist', 'tune_mode']]
        self.titles_dict = titles.to_dict()

        tunes = df.loc[:, ['tune_id', 'title_playlist']].drop_duplicates()
        self.tunes = tunes.set_index('tune_id').to_dict()

        titles_rows = titles.to_dict(orient='records')
        self._sectionid_to_section = []
        for i, row in enumerate(titles_rows):
            name = f"{row['title']}, section{row['section_id']} ({row['section_name']})"
            self._sectionid_to_section.append(name)

        self._sectionid_to_sectionlabel = []
        for i, row in enumerate(titles_rows):
            self._sectionid_to_sectionlabel.append(row['section_name'])

        self._title_to_sectionid = {}
        for row in titles.iterrows():
            title = row[1]['title_playlist']
            if title not in self._title_to_sectionid:
                self._title_to_sectionid[title] = [row[1]['id']]
            else:
                self._title_to_sectionid[title].append(row[1]['id'])

        self.test_tune_sectionid = []
        for title in _get_list_of_test_tunes():
            self.test_tune_sectionid.extend(self.title_to_sectionid(title))

        if not os.path.exists('output'):
            os.makedirs('output')
        if not os.path.exists('output/model'):
            os.makedirs('output/model')


    def sectionid_to_title(self, id):
        return self.titles_dict['title_playlist'][id]

    def sectionid_to_titleid(self, id):
        return self.titles_dict['tune_id'][id]

    def titleid_to_title(self, id):
        return self.tunes['title_playlist'][id]

    def title_to_titleid(self, id):
        return {v: k for k, v in self.tunes['title_playlist'].items()}

    def sectionid_to_section(self, id):
        return self._sectionid_to_section[id]

    def sectionid_to_sectionlabel(self, id):
        return self._sectionid_to_sectionlabel[id]

    def title_to_sectionid(self, id):
        return self._title_to_sectionid[id]


    def corpus(self):
        lines = self.df.loc[:, 'chords'].tolist()
        data = [line.split(' ') for line in lines]

        self.processed_corpus = []
        self.test_corpus = []

        # for line in data:
        for id, line in enumerate(data):
            tune_n = []
            if self.remove_repetitions:
                line = _remove_chord_repetitions(line)
            for n in self.ngrams:
                tune_n.extend(_make_ngrams(line, n=n))
            self.processed_corpus.append(tune_n)
            if id not in self.test_tune_sectionid:
                self.test_corpus.append(tune_n)

        for line in self.processed_corpus[:5]:
            print(line)

    def get_processed_corpus(self):
        return self.processed_corpus

    def get_test_corpus(self):
        return self.test_corpus


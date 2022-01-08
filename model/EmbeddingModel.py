import pandas as pd
from tqdm import tqdm
from model.PrepareData import PrepareData
from model.config import get_test_tunes, doc2vec_config
from gensim import corpora
from gensim.models import doc2vec


class EmbeddingModel(PrepareData):
    pass

    def get_tagged_documents(self, corpus, tag_sections_and_tunes=False):
        if tag_sections_and_tunes:
            print('Tagging input data with both section and tune information.')
        else:
            print('Tagging input data with section informaiton only.')

        for i, tokens in enumerate(corpus):
            if tag_sections_and_tunes:
                #yield doc2vec.TaggedDocument(tokens, [i, f'titleid_{sectionid_to_titleid[i]}'])
                yield doc2vec.TaggedDocument(tokens, [i])  # diatonic chord distance is a bit better
            else:
                yield doc2vec.TaggedDocument(tokens, [i])  # diatonic chord distance is a bit better


    def prepare_corpus(self, df_clean):

        doc_clean = list(df_clean['chords'])
        train_corpus = list(self.get_tagged_documents(doc_clean, doc2vec_config['general']['tag_sections_and_tunes']))
        return train_corpus


    def test_contrafacts(self, tunes, n=15):
        """
        Evaluates if the expected tune matches by either a tune similarity or section similarity match.
        """
        matches = 0
        number_of_sections = 0
        results = {}

        for tune, similar_tune in get_test_tunes():
            # loop over all sections of the tune
            section_matches = 0
            rank = 0
            score = 0
            for s1 in self.title_to_sectionid_unique_section(tune):
                print(f"{tune} - {similar_tune}")
                #print(f" s1: {s1}")

                id = self.df_train_test.loc[s1]['index']
                sims = self.doc2vec.dv.similar_by_key(id, topn=n)

                # check if the section matches the expected title; consider only the first N recommendations
                i = 0

                for id, value in sims:
                    sectionid = self.df_train_test.iloc[id].name
                    #print(f"   sim {self.sectionid_to_section(sectionid)}")
                    if self.sectionid_to_title(sectionid) == similar_tune:
                        section_matches += 1
                        print(
                            f"Found {tune} - {similar_tune} {self.sectionid_to_sectionlabel(sectionid)} with value {value}")
                        if value > score:
                            rank = i
                            score = value
                        break
                    i += 1

            # for each title, increase matches if at least one of the section matched the expected title
            if section_matches > 0:
                matches += 1
                results[f'{tune}, {similar_tune}'] = {'found': 1,
                                                      'score': score,
                                                      'rank': rank}
            else:
                results[f'{tune}, {similar_tune}'] = {'found': 0,
                                                      'score': 0,
                                                      'rank': 0}
        return matches, results

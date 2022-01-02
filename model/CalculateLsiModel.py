from model.BowModel import BowModel
from model.config import lsi_config, test_topN
from gensim.models.lsimodel import LsiModel
from gensim import similarities
from gensim.matutils import sparse2full
import pandas as pd
import numpy as np


class CalculateLsiModel(BowModel):
    pass


    def calculate_lsi_model(self):
        print('\n*** Calculate LSI Model ***')
        self.train_dictionary, self.train_bow_corpus = self.prepare_corpus(self.train_corpus)
        self.dictionary, self.bow_corpus = self.prepare_corpus(self.processed_corpus)

        #***
        ### here we're using the dictionary of the full dataset! Gives a bit better results!
        #self.test_bow_corpus = [self.dictionary.doc2bow(text) for text in self.test_corpus]
        #***


        num_topics = lsi_config['num_topics']

        # TODO: with test_bow_corpus and test_dictionary, inf values occur at Topic 4!! for section 1040, 2068, 2388, 2803, 3138
        self.lsi = LsiModel(self.bow_corpus,
                       id2word=self.dictionary,
                       num_topics=num_topics)

        print(self.lsi)

    def store_model(self):
        self.lsi.save('output/model/lsi.model')

    def load_model(self):
        self.lsi = LsiModel.load('output/model/lsi.model')
        self.dictionary = self.lsi.id2word

    def store_similarity_matrix(self):
        print('\n*** Calculate and store Similarity Matrix ***')
        index_path = 'output/model'

# TODO overflow errors with the memory-optimized version
#        self.index_lsi = similarities.Similarity('lsi_index',
#                                                 self.lsi[self.bow_corpus],
#                                                 num_features=len(self.dictionary))

        self.index_lsi = similarities.MatrixSimilarity(self.lsi[self.bow_corpus],
                                                 num_features=len(self.dictionary))

        self.index_lsi.save("output/model/lsi_matrixsim.index")

    def load_similarity_matrix(self):
        self.index_lsi = similarities.MatrixSimilarity.load("output/model/lsi_matrixsim.index")

    def lsi_test_contrafacts(self):
        matches, results = self.test_contrafacts(self.lsi, self.index_lsi, N=test_topN)
        return matches, results


    def get_tune_vectors(self):
        tunes_matrix = []
        tune_section = []

        tunes = list(self.tunes['title_playlist'].values())
        for tune in tunes:
            for s1 in self.title_to_sectionid_unique_section(tune):
                query = self.processed_corpus.iloc[self.sectionid_to_row_id(s1), 1]
                query_bow = self.dictionary.doc2bow(query)
                V = sparse2full(self.lsi[query_bow], len(self.lsi.projection.s)).T / self.lsi.projection.s
                tunes_matrix.append(V)
                tune_section.append(f"{tune} ({self.sectionid_to_sectionlabel(s1)})")

        return pd.DataFrame(tunes_matrix)


    def get_similar_tunes(self, sectionid, topn=None):
        tune = self.df_section.query(f'id == {sectionid}')
        query = self.preprocess_input(list(tune['chords'])[0])
        query_bow = self.dictionary.doc2bow(query)

        # perform a similarity query against the corpus
        similarities = self.index_lsi[self.lsi[query_bow]]
        sims = sorted(enumerate(similarities), key=lambda item: -item[1])

        if topn is None:
            return sims
        else:
            return sims[1:topn + 1]


from model.BowModel import BowModel
from model.config import preprocess_config
from gensim.models.tfidfmodel import TfidfModel
from gensim import similarities
from gensim.matutils import sparse2full
import pandas as pd


class CalculateTfidfModel(BowModel):
    def __init__(self, chords_preprocessing, ngrams):
        self.model_name = 'tfidf'
        super().__init__(chords_preprocessing, ngrams)
        self.model_config = {}
        filename = f'output/model/{self.model_name}_{self.chords_preprocessing}_{self.get_ngrams_as_str()}'
        self.model_filename = f'{filename}.model'
        self.index_filename = f'{filename}.index'


    def calculate_tfidf_model(self):
        print('\n*** Calculate TF-IDF Model ***')
        self.train_dictionary, self.train_bow_corpus = self.prepare_dict_and_corpus(self.df_train)
        self.test_bow_corpus = self.prepare_corpus(self.df_test, self.train_dictionary)

        self.tfidf = TfidfModel(self.train_bow_corpus,
                            id2word=self.train_dictionary)

        print(self.tfidf)

    def store_model(self):
        self.tfidf.save(self.model_filename)

    def load_model(self):
        self.tfidf = TfidfModel.load(self.model_filename)
        # TODO get rid of self.train_dictionary and use self.tfidf.id2word instead?
        self.train_dictionary = self.tfidf.id2word


    def store_similarity_matrix(self):
        print('\n*** Calculate and store Similarity Matrix ***')

        print("Store MatrixSimilarity for TEST and TRAIN")
        self.index_tfidf = similarities.MatrixSimilarity(self.tfidf[self.train_bow_corpus + self.test_bow_corpus],
                                                       num_features=len(self.train_dictionary))
        # Store index
        self.index_tfidf.save(self.index_filename)

    def load_similarity_matrix(self):
        self.index_tfidf = similarities.MatrixSimilarity.load(self.index_filename)

    def tfidf_test_contrafacts(self):
        matches, results = self.test_contrafacts(self.tfidf, self.index_tfidf, n=preprocess_config['test_topN'])
        return matches, results

    def get_tune_similarity(self):
        df_sim = self.get_sim_scores(self.tfidf, self.index_tfidf, topn=preprocess_config['test_topN'])
        return df_sim

    def get_similar_tunes(self, sectionid, topn=None):

        query = self.df_train_test.loc[sectionid]['chords']
        query_bow = self.train_dictionary.doc2bow(query)

        # perform a similarity query against the corpus
        similarities = self.index_tfidf[self.tfidf[query_bow]]
        sims = sorted(enumerate(similarities), key=lambda item: -item[1])

        if topn is None:
            return sims
        else:
            return sims[1:topn + 1]

    def get_vocab_info(self):
        return self.get_vocab_counts(self.tfidf)
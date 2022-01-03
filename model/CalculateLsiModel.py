from model.BowModel import BowModel
from model.config import lsi_config, test_topN
from gensim.models.lsimodel import LsiModel
from gensim import similarities
from gensim.matutils import sparse2full
import pandas as pd


class CalculateLsiModel(BowModel):
    pass

    def calculate_lsi_model(self):
        print('\n*** Calculate LSI Model ***')
        self.train_dictionary, self.train_bow_corpus = self.prepare_dict_and_corpus(self.df_train)
        self.test_bow_corpus = self.prepare_corpus(self.df_test, self.train_dictionary)

        num_topics = lsi_config['num_topics']

        self.lsi = LsiModel(self.train_bow_corpus,
                            id2word=self.train_dictionary,
                            num_topics=num_topics)

        print(self.lsi)

    def store_model(self):
        self.lsi.save('output/model/lsi.model')

    def load_model(self):
        self.lsi = LsiModel.load('output/model/lsi.model')

        # TODO get rid of self.train_dictionary and use self.lsi.id2word instead?
        self.train_dictionary = self.lsi.id2word

    def add_test_documents_to_model(self):
        print(f"LSI Model processed {self.lsi.docs_processed} sections so far. ")
        self.lsi.add_documents(self.test_bow_corpus)
        print(f"Adding test set: now the Model processed {self.lsi.docs_processed}.")


    def store_similarity_matrix(self):
        print('\n*** Calculate and store Similarity Matrix ***')
        index_path = 'output/model'

        # TODO overflow errors with the memory-optimized version
        #        self.index_lsi = similarities.Similarity('lsi_index',
        #                                                 self.lsi[self.bow_corpus],
        #                                                 num_features=len(self.dictionary))


        if self.lsi.docs_processed == len(self.train_bow_corpus):
            print("Store MatrixSimilarity for TRAIN only")
            self.index_lsi = similarities.MatrixSimilarity(self.lsi[self.train_bow_corpus],
                                                           num_features=len(self.train_dictionary))

        elif self.lsi.docs_processed == len(self.train_bow_corpus + self.test_bow_corpus):
            print("Store MatrixSimilarity for TEST and TRAIN")
            self.index_lsi = similarities.MatrixSimilarity(self.lsi[self.train_bow_corpus + self.test_bow_corpus],
                                                       num_features=len(self.train_dictionary))
        else:
            assert(False)

        self.index_lsi.save("output/model/lsi_matrixsim.index")

    def load_similarity_matrix(self):
        self.index_lsi = similarities.MatrixSimilarity.load("output/model/lsi_matrixsim.index")

    def lsi_test_contrafacts(self):
        matches, results = self.test_contrafacts(self.lsi, self.index_lsi, n=test_topN)
        return matches, results

    def get_train_tune_vectors(self):
        tunes_matrix = []

        for s1 in self.df_train.index:
            query = self.df_train.loc[s1]['chords']
            query_bow = self.train_dictionary.doc2bow(query)
            V = sparse2full(self.lsi[query_bow], len(self.lsi.projection.s)).T / self.lsi.projection.s
            tunes_matrix.append(V)

        _df = pd.DataFrame(tunes_matrix)
        _df['sectionid'] = self.df_train.index
        _df.set_index('sectionid', inplace=True)
        return _df


    def get_similar_tunes(self, sectionid, topn=None):

        query = self.df_train_test.loc[sectionid]['chords']
        query_bow = self.train_dictionary.doc2bow(query)

        # perform a similarity query against the corpus
        similarities = self.index_lsi[self.lsi[query_bow]]
        sims = sorted(enumerate(similarities), key=lambda item: -item[1])

        if topn is None:
            return sims
        else:
            return sims[1:topn + 1]

from model.BowModel import BowModel
from model.config import preprocess_config
from gensim.models.lsimodel import LsiModel
from gensim import similarities
from gensim.matutils import sparse2full
import pandas as pd


class CalculateLsiModel(BowModel):
    def __init__(self, chords_preprocessing, ngrams):
        self.model_name = 'lsi'
        super().__init__(chords_preprocessing, ngrams)
        self.model_config = {
            'num_topics': 100  # 22, # 100 gives a better value for the contrafacts test
        }
        self.model_filename = f'output/model/{self.model_name}_{self.chords_preprocessing}_{self.get_ngrams_as_str()}.model'


    def calculate_lsi_model(self):
        print('\n*** Calculate LSI Model ***')
        self.train_dictionary, self.train_bow_corpus = self.prepare_dict_and_corpus(self.df_train)
        self.test_bow_corpus = self.prepare_corpus(self.df_test, self.train_dictionary)

        self.lsi = LsiModel(self.train_bow_corpus,
                            id2word=self.train_dictionary,
                            num_topics=self.model_config['num_topics'])

        print(self.lsi)

    def store_model(self):
        self.lsi.save(f'output/model/{self.model_name}_{self.chords_preprocessing}_{self.get_ngrams_as_str()}.model')

    def load_model(self):
        self.lsi = LsiModel.load(f'output/model/{self.model_name}_{self.chords_preprocessing}_{self.get_ngrams_as_str()}.model')

        # TODO get rid of self.train_dictionary and use self.lsi.id2word instead?
        self.train_dictionary = self.lsi.id2word

    def add_test_documents_to_model(self):
        print(f"LSI Model processed {self.lsi.docs_processed} sections so far. ")
        self.lsi.add_documents(self.test_bow_corpus)
        print(f"Adding test set: now the Model processed {self.lsi.docs_processed}.")


    def store_similarity_matrix(self):
        print('\n*** Calculate and store Similarity Matrix ***')

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

        # Note: If the matrix should not fit into RAM anymore, this would be the memory-optimized version:
        # self.index_lsi = similarities.Similarity('lsi_index',
        #                                          self.lsi[self.bow_corpus],
        #                                          num_features=len(self.dictionary))
        # Store index
        self.index_lsi.save(f"output/model/{self.model_name}_matrixsim_{self.chords_preprocessing}.index")

    def load_similarity_matrix(self):
        self.index_lsi = similarities.MatrixSimilarity.load(f"output/model/lsi_matrixsim_{self.chords_preprocessing}.index")

    def lsi_test_contrafacts(self):
        matches, results = self.test_contrafacts(self.lsi, self.index_lsi, n=preprocess_config['test_topN'])
        return matches, results

    def get_tune_similarity(self):
        df_sim = self.get_sim_scores(self.lsi, self.index_lsi, topn=preprocess_config['test_topN'])
        return df_sim

    def get_train_tune_vectors(self):
        tunes_matrix = []

        for s1 in self.df_train_test.index:
            query = self.df_train_test.loc[s1]['chords']
            query_bow = self.train_dictionary.doc2bow(query)
            V = sparse2full(self.lsi[query_bow], len(self.lsi.projection.s)).T / self.lsi.projection.s
            tunes_matrix.append(V)

        _df = pd.DataFrame(tunes_matrix)
        _df['sectionid'] = self.df_train_test.index
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

    def get_vocab_info(self):
        return self.get_vocab_counts(self.lsi)
from model.EmbeddingModel import EmbeddingModel
from model.config import preprocess_config
from gensim.models.doc2vec import Doc2Vec
from gensim import similarities


class CalculateDoc2VecModel(EmbeddingModel):
    def __init__(self, chords_preprocessing):
        self.model_name = 'doc2vec'
        super().__init__(chords_preprocessing)
        self.model_config = {
                'dm': 0,
                'dbow_words': 1,
                'vector_size': 300,
                'window': 2,
                'epochs': 40,
                # 'workers': 1,
                'min_count': 1,
                'negative': 10,
                'sample': 0.1,
                'seed': 42,
                'hs': 0,
        }

    def calculate_doc2vec_model(self):
        print('\n*** Calculate Doc2Vec Model ***')
        self.train_corpus = self.prepare_corpus(self.df_train_test)

        self.doc2vec = Doc2Vec(self.train_corpus,
                               **self.model_config
                               )

        print(self.doc2vec)

    def store_model(self):
        self.doc2vec.save(f'output/model/{self.model_name}_{self.chords_preprocessing}.model')

    def load_model(self):
        self.doc2vec = Doc2Vec.load(f'output/model/{self.model_name}_{self.chords_preprocessing}.model')

    def doc2vec_test_contrafacts(self):
        matches, results = self.test_contrafacts(self.doc2vec, n=preprocess_config['test_topN'])
        return matches, results

    def get_tune_similarity(self):
        df_sim = self.get_sim_scores(self.doc2vec, topn=preprocess_config['test_topN'])
        return df_sim
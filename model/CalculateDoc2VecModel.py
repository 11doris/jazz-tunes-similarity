from model.EmbeddingModel import EmbeddingModel
from model.config import preprocess_config, doc2vec_config
from gensim.models.doc2vec import Doc2Vec
from gensim import similarities


class CalculateDoc2VecModel(EmbeddingModel):
    def __init__(self, chords_preprocessing):
        self.model_name = 'doc2vec'
        super().__init__(chords_preprocessing)

    def calculate_doc2vec_model(self):
        print('\n*** Calculate Doc2Vec Model ***')
        self.train_corpus = self.prepare_corpus(self.df_train)

        self.doc2vec = Doc2Vec(self.train_corpus,
                               **doc2vec_config['model']
                )

        print(self.doc2vec)

    def store_model(self):
        self.doc2vec.save(f'output/model/{self.model_name}_{self.chords_preprocessing}.model')

    def load_model(self):
        self.doc2vec = Doc2Vec.load(f'output/model/{self.model_name}_{self.chords_preprocessing}.model')

    def doc2vec_test_contrafacts(self):
        matches, results = self.test_contrafacts(self.doc2vec, n=preprocess_config['test_topN'])
        return matches, results
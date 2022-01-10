from model.EmbeddingModel import EmbeddingModel
from model.config import preprocess_config
from gensim.models.doc2vec import Doc2Vec
from tqdm import tqdm
from collections import Counter

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
        self.train_corpus = self.prepare_corpus(self.df_train)

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

    def self_similarity_test(self):
        # Evaluate self-similarity of the sections
        print("\nEvaluating self-similarity for the sections using the embedding:")
        ranks = []
        train_corpus = self.get_train_corpus().reset_index()
        for doc_id in tqdm(range(len(train_corpus))):
            inferred_vector = self.doc2vec.infer_vector(train_corpus.loc[doc_id]['chords'])
            sims = self.doc2vec.dv.most_similar([inferred_vector], topn=len(self.doc2vec.dv))
            rank = [docid for docid, sim in sims].index(doc_id)
            ranks.append(rank)

        # count in which rank the sections are self-similar
        counter = Counter(ranks)
        self_similar1 = counter[0] / len(train_corpus)
        self_similar2 = (counter[0] + counter[1]) / len(train_corpus)
        return counter, [self_similar1, self_similar2]
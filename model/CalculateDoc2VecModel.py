from model.EmbeddingModel import EmbeddingModel
from model.config import preprocess_config
from gensim.models.doc2vec import Doc2Vec
from tqdm import tqdm
from collections import Counter

class CalculateDoc2VecModel(EmbeddingModel):
    def __init__(self, chords_preprocessing, ngrams):
        self.model_name = 'doc2vec'
        super().__init__(chords_preprocessing, ngrams)
        self.model_config = {
                'dm': 0,
                'dbow_words': 1,
                'vector_size': 300,
                'window': 3,
                'epochs': 50,
                'min_count': 20,
                'negative': 14,
                'sample': 0.001,
                'seed': 42,
                'hs': 1,
        }
        self.model_filename = f'output/model/{self.model_name}_{self.chords_preprocessing}_{self.get_ngrams_as_str()}.model'


    def calculate_doc2vec_model(self):
        print('\n*** Calculate Doc2Vec Model ***')
        self.train_corpus = self.prepare_corpus(self.df_train)

        self.doc2vec = Doc2Vec(self.train_corpus,
                               **self.model_config
                               )
        print(self.doc2vec)

    def store_model(self):
        self.doc2vec.save(f'output/model/{self.model_name}_{self.chords_preprocessing}_{self.get_ngrams_as_str()}.model')

    def load_model(self):
        self.doc2vec = Doc2Vec.load(f'output/model/{self.model_name}_{self.chords_preprocessing}_{self.get_ngrams_as_str()}.model')

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

    def get_vocab_info(self):
        return self.get_vocab_counts(self.doc2vec)

    def chord_analogy(self, n=5):
        model = self.doc2vec

        word_analogies_file = 'tests/fixtures/test_chord_analogies.txt'
        score = round(model.wv.evaluate_word_analogies(word_analogies_file)[0], 4)
        print(score)

        with open('tests/fixtures/test_chord_analogies.txt') as f:
            lines = f.read().splitlines()

        pairs = [line.split(" ") for line in lines]
        perfect_match = 0
        topn_match = 0
        for pair in pairs:
            if pair[0] == ':':
                continue
            else:
                sims = model.wv.most_similar(positive=[pair[1], pair[2]], negative=[pair[0]], topn=n)
                if sims[0][0] == pair[3]:
                    # print(f"Found:     {pair[0]}-{pair[1]} and {pair[2]}-{pair[3]}")
                    perfect_match += 1
                    topn_match += 1
                else:
                    if pair[3] in [item[0] for item in sims]:
                        # print(f"Top {n}:     {pair[0]}-{pair[1]} and {pair[2]}-{pair[3]}")
                        topn_match += 1
                    # else:
                    #    print(f"Not found: {pair[0]}-{pair[1]} and {pair[2]}-{pair[3]}")

        prop_perfect = perfect_match / len(pairs)
        prop_topn = topn_match / len(pairs)

        return {
            'perfect': prop_perfect,
            'topn': prop_topn,
        }

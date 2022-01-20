from model.EmbeddingModel import EmbeddingModel
from model.config import preprocess_config
from gensim.models.doc2vec import Doc2Vec
from tqdm import tqdm
from collections import Counter


def _evaluate_word_analogies(section):
    correct = len(section['correct'])
    topn = len(section['topn'])
    incorrect = len(section['incorrect'])

    if correct + topn + incorrect > 0:
        perfect = correct / (correct + topn + incorrect)
        topn = topn / (correct + topn + incorrect)
        return perfect, topn


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
                'min_count': 30,
                'negative': 12,
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

        analogies = 'tests/fixtures/test_chord_analogies.txt'
        sections = []
        scores = []
        section = None

        with open(analogies, 'rb') as fin:
            for line_no, line in enumerate(fin):
                line = line.decode('unicode-escape')
                if line.startswith(': '):
                    # a new section starts => store the old section
                    if section:
                        sections.append(section)
                        perfect, topn = _evaluate_word_analogies(section)
                        scores.append({'section': section['section'], 'correct': perfect, 'topn': topn,
                                       'incorrect': 1 - perfect - topn})
                        print(
                            f"{section['section']}, {100 * perfect:.2f}% perfect match, {100 * topn:.2f}% top {n} match")

                    section = {'section': line.lstrip(': ').strip(), 'correct': [], 'topn': [], 'incorrect': []}
                else:
                    perfect_match = 0
                    topn_match = 0
                    pair = line.strip().split(" ")
                    sims = self.doc2vec.wv.most_similar(positive=[pair[1], pair[2]], negative=[pair[0]], topn=n)
                    if sims[0][0] == pair[3]:
                        # print(f"Found:     {pair[0]}-{pair[1]} and {pair[2]}-{pair[3]}")
                        section['correct'].append(pair)
                        perfect_match += 1
                        topn_match += 1
                    else:
                        if pair[3] in [item[0] for item in sims]:
                            # print(f"Top {n}:     {pair[0]}-{pair[1]} and {pair[2]}-{pair[3]}")
                            topn_match += 1
                            section['topn'].append(pair)
                        else:
                            section['incorrect'].append(pair)
            # append last section
            if section:
                sections.append(section)
                perfect, topn = _evaluate_word_analogies(section)
                scores.append({'section': section['section'], 'correct': perfect, 'topn': topn, 'incorrect': 1 - perfect - topn})
                print(f"{section['section']}, {100 * perfect:.2f}% perfect match, {100 * topn:.2f}% top {n} match")

                # append overall result
                correct = 0.0
                topn = 0.0
                incorrect = 0.0
                for score in scores:
                    correct += score['correct']
                    topn += score['topn']
                    incorrect += score['incorrect']
                overall = {'section': 'overall', 'correct': correct/len(scores), 'topn': topn/len(scores), 'incorrect': incorrect/len(scores)}

        print()
        print("Found these perfect matches for chord analogies:")
        for section in sections:
            print(f"{section['section']}: ")
            for analogy in section['correct']:
                print(f"\t{analogy}")

        print()
        print(f"Found these top {n} matches for chord analogies:")
        for section in sections:
            print(f"{section['section']}: ")
            for analogy in section['topn']:
                print(f"\t{analogy}")

        print()
        print("Scores")
        print()
        for score in scores:
            print(score)
        print('Overall:')
        print(overall)

        return scores, overall

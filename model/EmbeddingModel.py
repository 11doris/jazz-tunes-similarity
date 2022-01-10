import pandas as pd
from tqdm import tqdm
from model.PrepareData import PrepareData
from model.config import get_test_tunes, preprocess_config
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
        train_corpus = list(self.get_tagged_documents(doc_clean))
        return train_corpus


    def get_sim_scores(self, model, topn=preprocess_config['test_topN']):

        dict_sim = {
            'reference_title': [],
            'reference_titleid': [],
            'ref_sectionid': [],
            'ref_section': [],
            'ref_section_label': [],
            'similar_title': [],
            'similar_titleid': [],
            'similar_sectionid': [],
            'similar_section': [],
            'similar_section_label': [],
            'score': [],
        }

        tunes = list(self.tunes['title_playlist'].values())

        # # for debugging only
        # tunes = [
        #     "Sweet Sue, Just You [jazz1350]",
        #     "On The Sunny Side Of The Street [jazz1350]",
        #     "These Foolish Things [jazz1350]",
        #     "Blue Moon [jazz1350]",
        #     "I Got Rhythm [jazz1350]",
        # ]

        for tune in tqdm(tunes):
            for s1 in self.title_to_sectionid_unique_section(tune):

                id = self.df_train_test.loc[s1]['index']

                # check if the current tune belongs to the training set, then we can directly access the embedding vector
                if id in model.dv.index_to_key:
                    sims = model.dv.similar_by_key(id, topn=topn)
                else:
                    # infer the embedding vector for the tune which is in test set
                    vector = self.doc2vec.infer_vector(self.df_train_test.loc[s1]['chords'])
                    sims = self.doc2vec.dv.similar_by_vector(vector, topn=topn)

                n = 0
                for id, s2_score in sims:
                    s2 = self.get_train_test_sectionid(id)
                    # don't count self-similarity between sections of the same tune
                    if s2 not in self.title_to_sectionid(tune):
                        # print(f"\t{s2_score:.3f} {sectionid_to_section[s2]}")
                        n += 1

                        dict_sim['reference_title'].append(tune)
                        dict_sim['reference_titleid'].append(self.title_to_titleid(tune))
                        dict_sim['ref_sectionid'].append(s1)
                        dict_sim['ref_section'].append(self.sectionid_to_section(s1))
                        dict_sim['ref_section_label'].append(self.sectionid_to_sectionlabel(s1))
                        dict_sim['similar_title'].append(self.sectionid_to_title(s2))
                        dict_sim['similar_titleid'].append(self.sectionid_to_titleid(s2))
                        dict_sim['similar_sectionid'].append(s2)
                        dict_sim['similar_section'].append(self.sectionid_to_section(s2))
                        dict_sim['similar_section_label'].append(self.sectionid_to_sectionlabel(s2))
                        dict_sim['score'].append(s2_score)

        df_sim = pd.DataFrame.from_dict(dict_sim)

        return df_sim

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
                #print(f"{tune} - {similar_tune}")
                #print(f" s1: {s1}")

                vector = self.doc2vec.infer_vector(self.df_train_test.loc[s1]['chords'])
                sims = self.doc2vec.dv.similar_by_vector(vector, topn=n)

                # check if the section matches the expected title; consider only the first N recommendations
                i = 0

                for id, value in sims:
                    sectionid = self.df_train_test.iloc[id].name
                    #print(f"   sim {self.sectionid_to_section(sectionid)}")
                    if self.sectionid_to_title(sectionid) == similar_tune:
                        section_matches += 1
                        # print(f"Found {tune} - {similar_tune} {self.sectionid_to_sectionlabel(sectionid)} with value {value}")
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

    def get_train_tune_vectors(self):
        tunes_matrix = []
        model = self.doc2vec
        for s1 in self.df_train_test.index:
            id = self.df_train_test.loc[s1]['index']

            if id in model.dv.index_to_key:
                vector = model.dv.vectors[id]
            else:
                # infer the embedding vector for the tune which is in test set
                vector = self.doc2vec.infer_vector(self.df_train_test.loc[s1]['chords'])
            tunes_matrix.append(vector)

        _df = pd.DataFrame(tunes_matrix)
        _df['sectionid'] = self.df_train_test.index
        _df.set_index('sectionid', inplace=True)
        return _df
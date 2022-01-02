import pandas as pd
from tqdm import tqdm
from model.PrepareData import PrepareData
from model.config import get_test_tunes, no_below
from gensim import corpora


class BowModel(PrepareData):
    pass

    def prepare_corpus(self, df_clean):
        """
        Input  : cleaned tunes
        Purpose: create term dictionary of our courpus and Converting list of documents (corpus) into Document Term Matrix
        Output : term dictionary and Document Term Matrix
        """
        doc_clean = list(df_clean['chords'])
        # Creating the term dictionary of our courpus, where every unique term is assigned an index.
        dic = corpora.Dictionary(doc_clean)
        # Filter out words that occur only in a few documents.
        dic.filter_extremes(no_below=no_below, no_above=1.0)

        # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
        doc_term_matrix = [dic.doc2bow(text) for text in doc_clean]

        # generate LDA model
        return dic, doc_term_matrix


    def get_sim_scores(self, topn=50):

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
                query = self.df_test.iloc[self.sectionid_to_row_id(s1), 1]
                query_bow = self.dictionary.doc2bow(query)

                # perform a similarity query against the corpus
                similarities = self.index_lsi[self.lsi[query_bow]]
                sims = sorted(enumerate(similarities), key=lambda item: -item[1])

                n = 0
                for id, s2_score in sims:
                    # store the top N best results
                    if n >= topn:
                        break

                    s2 = self.row_id_to_sectionid(id)
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


    def test_contrafacts(self, model, index, N=15):
        matches = 0
        number_of_sections = 0
        results = {}

        for tune, similar_tune in get_test_tunes():

            # loop over all sections of the tune
            section_matches = 0
            rank = 0
            score = 0
            for s1 in self.title_to_sectionid_unique_section(tune):
                query = self.df_test.loc[s1]['chords']
                query_bow = self.train_dictionary.doc2bow(query)

                # perform a similarity query against the corpus
                similarities = index[model[query_bow]]
                sims = sorted(enumerate(similarities), key=lambda item: -item[1])
                print(f"{tune} s1: {s1}")
                #print(f"similar_tune: {similar_tune}, {title_to_sectionid[similar_tune]}")
                # print(sims)
                # print(len(sims))

                # check if the section matches the expected title; consider only the first N recommendations
                i = 0
				
				# TODO!! because corpus is updated, there is a new mapping needed!
                _map_id_to_sectionid = list(self.df_train.index) + list(self.df_test.index)
                for id, value in sims:
                    if i >= N:
                        break
                    sectionid = _map_id_to_sectionid[id]
                    if self.sectionid_to_title(sectionid) == similar_tune:
                        section_matches += 1
                        print(
                            f"Found {tune} - {similar_tune} {self.sectionid_to_sectionlabel(sectionid)} with value {value}")
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
                score = 0
                for sectionid in self.title_to_sectionid_unique_section(similar_tune):
                    sim_value = similarities[self.sectionid_to_row_id(sectionid)]
                    score = sim_value if sim_value > score else score

                results[f'{tune}, {similar_tune}'] = {'found': 0,
                                                      'score': score,
                                                      'rank': rank}

        return matches, results

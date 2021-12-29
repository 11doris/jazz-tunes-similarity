import pandas as pd
from tqdm import tqdm
from model.PrepareData import PrepareData
from model.config import get_test_tunes, no_below
from gensim import corpora


class BowModel(PrepareData):
    pass

    def prepare_corpus(self, doc_clean):
        """
        Input  : cleaned tunes
        Purpose: create term dictionary of our courpus and Converting list of documents (corpus) into Document Term Matrix
        Output : term dictionary and Document Term Matrix
        """
        # Creating the term dictionary of our courpus, where every unique term is assigned an index. dictionary = corpora.Dictionary(doc_clean)
        dic = corpora.Dictionary(doc_clean)
        # Filter out words that occur less than 20 documents.
        dic.filter_extremes(no_below=no_below, no_above=1.0)

        # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
        doc_term_matrix = [dic.doc2bow(text) for text in doc_clean]

        # generate LDA model
        return dic, doc_term_matrix


    def get_sim_scores(self, index, model, topn=50):

        df_sim = pd.DataFrame(columns=['reference_title',
                                       'reference_titleid',
                                       'similar_title',
                                       'similar_titleid',
                                       'ref_section',
                                       'ref_section_label',
                                       'ref_sectionid',
                                       'similar_section',
                                       'similar_section_label',
                                       'similar_sectionid',
                                       'score',
                                       ])

        for tune in tqdm(get_test_tunes()):
            for s1 in self.title_to_sectionid(tune):

                query = self.processed_corpus[s1]
                query_bow = self.dictionary.doc2bow(query)

                # perform a similarity query against the corpus
                similarities = index[model[query_bow]]
                sims = sorted(enumerate(similarities), key=lambda item: -item[1])

                n = 0
                for s2, s2_score in sims:

                    # store the top N best results
                    if n > topn:
                        break
                    # don't count self-similarity between sections of the same tune
                    if s2 not in self.title_to_sectionid(tune):
                        # print(f"\t{s2_score:.3f} {sectionid_to_section[s2]}")
                        n += 1
                        df_sim.loc[len(df_sim)] = [tune,
                                                   self.title_to_titleid(tune),
                                                   self.sectionid_to_title(s2),
                                                   self.sectionid_to_titleid(s2),
                                                   self.sectionid_to_section(s1),
                                                   self.sectionid_to_sectionlabel(s1),
                                                   s1,
                                                   self.sectionid_to_section(s2),
                                                   self.sectionid_to_sectionlabel(s2),
                                                   s2,
                                                   s2_score,
                                                   ]
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

            for s1 in self.title_to_sectionid(tune):
                query = self.processed_corpus[s1]
                query_bow = self.dictionary.doc2bow(query)

                # perform a similarity query against the corpus
                similarities = index[model[query_bow]]
                sims = sorted(enumerate(similarities), key=lambda item: -item[1])
                # print(f"s1: {s1}")
                # print(f"similar_tune: {similar_tune}, {title_to_sectionid[similar_tune]}")
                # print(sims)
                # print(len(sims))

                # check if the section matches the expected title; consider only the first N recommendations
                i = 0
                for sectionid, value in sims:
                    if i >= N:
                        break
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
                for sectionid in self.title_to_sectionid(similar_tune):
                    sim_value = similarities[sectionid]
                    score = sim_value if sim_value > score else score

                results[f'{tune}, {similar_tune}'] = {'found': 0,
                                                      'score': score,
                                                      'rank': rank}

        return matches, results

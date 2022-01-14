import pandas as pd
from dataset.utils import set_pandas_display_options
from model.CalculateDoc2VecModel import *
import numpy as np
import zipfile
import plotly.express as px


def diatonic_chords(doc2vecObj, preprocessing):
    model = doc2vecObj.doc2vec
    if 1 in preprocess_config['ngrams']:
        if preprocessing == 'chordsBasic':
            ref = 'F'
        else:
            ref = 'FM7'

        print(f"\nMost similar to {ref}:")
        for t in model.wv.similar_by_word(ref, topn=20):
            print(t)


def corpus_chord_ngram(doc2vecObj, ngrams):
    _df = pd.DataFrame(columns=['sectionid', 'chords'])
    list_corpus_chords = []
    list_sectionid = []

    # for each unique section of a tune, process the chords
    for id, line in doc2vecObj.df_section.iterrows():
        sectionid = line['sectionid']
        tune_n = doc2vecObj.preprocess_input(line['chords'], ngrams=ngrams)

        list_corpus_chords.append(tune_n)
        list_sectionid.append(sectionid)

    _df = pd.DataFrame(list(zip(list_sectionid, list_corpus_chords)),
                       columns=['sectionid', 'chords'])
    _df = _df.set_index('sectionid')
    return _df


def do_chord_analogy_test(model, pairs):
    n = 5
    perfect_match = 0
    topn_match = 0
    for pair in pairs:
        #print(f"{pair[0]}-{pair[1]} is like {pair[2]} to ?")
        sims = model.doc2vec.wv.most_similar(positive=[pair[1], pair[2]], negative=[pair[0]], topn=n)
        if sims[0][0] == pair[3]:
            print(f"Perfect: {pair[0]}-{pair[1]} is like {pair[2]}-{pair[3]}")
            perfect_match += 1
            topn_match += 1
        else:
            if pair[3] in [item[0] for item in sims]:
                print(f"Top {n}: {pair[0]}-{pair[1]} is like {pair[2]}-{pair[3]}")
                topn_match += 1

    print(f"Perfect matches: {100*perfect_match/len(pairs):.3}%")
    print(f"Top {n} matches: {100 * topn_match / len(pairs):.3}%")


def get_analogy_accuracy(model):
    score = round(model.doc2vec.wv.evaluate_word_analogies("chords_analogy.txt", case_insensitive=False)[0], 4)
    print(score)


def raw_chords_to_df(df):
    tunes = df['chords'].to_list()
    tunes_chords = [item for tune in tunes for item in tune]
    counts = Counter(tunes_chords)
    df_count = pd.DataFrame(counts.items(),
                            columns=['chord', 'count']).sort_values(by='count', ascending=False)

    return df_count


if __name__ == "__main__":
    set_pandas_display_options()

    for p in ['chordsBasic']:  # , 'chordsSimplified']:
        print(f'*** Chord Preprocessing: {p} ***')

        # initialize model with the chords preprocessing method
        mod = CalculateDoc2VecModel(p)
        mod.load_model()

        diatonic_chords(mod, p)

        df = corpus_chord_ngram(mod, ngrams=[1, 2, 3, 4, 5, 6, 7, 8])

        # pairs = [
        #     ['G7', 'C', 'C7', 'F'],
        #     ['G', 'C', 'C', 'F'],
        #     ['Am', 'C', 'Cm', 'Eb']
        # ]
        #
        # with open('chords_analogy2.txt') as f:
        #     lines = f.read().splitlines()
        #
        # pairs = [line.split(" ") for line in lines]
        #
        # do_chord_analogy_test(mod, pairs)

        print()
        df_chords = raw_chords_to_df(df)
        df_chords['ngram'] = df_chords['chord'].str.count('-') + 1
        df_chords.to_csv('chord_ngrams.csv')

        #df_chords.sort_values(by=['count'], ascending=False, inplace=True)
        df_chords_top = df_chords.query('count > 100')

        # fig = px.bar(df_chords_top,
        #              x='count', y='chord',
        #              orientation='h',
        #              log_x=True)
        # fig.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})
        # fig.show()

        print()
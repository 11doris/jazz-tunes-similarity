import pandas as pd
from dataset.utils import set_pandas_display_options
from model.CalculateDoc2VecModel import *
from model.UseWandB import *
import numpy as np
import zipfile


def do_contrafacts_test(doc2VecObject):
    # test how many of the contrafacts are found
    matches, results = doc2VecObject.doc2vec_test_contrafacts()

    for rr, val in results.items():
        if val == 0:
            print(f"{val}: {rr}")

    df_sim = pd.DataFrame.from_dict(results, orient='index')
    df_sim = df_sim.reset_index()
    df_sim.sort_values('index')
    print(df_sim)
    print()
    print(f"Found matches: {matches} out of {len(results)}: {100 * matches / len(results):.3f}%")

    wandb.store_results(doc2VecObject.model_name, matches, df_sim, doc2VecObject.model_config)


def diatonic_chords(doc2vecObj, preprocessing):

    model = doc2vecObj.doc2vec
    if 1 in preprocess_config['ngrams']:
        if preprocessing == 'rootAndDegreesPlus':
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
    return _df


def plot_weights(doc2vecObj, preprocessing):
    from sklearn.manifold import TSNE
    import plotly.express as px

    model = doc2vecObj.doc2vec

    # input data: vectors for all tokens
    weights = model.wv.vectors
    chord_names = model.wv.index_to_key

    # only do this when the vocabulary is not too big....
    if len(weights) > 100:
        print("Reducing the T-SNE plot to C since the full plot will be too cluttered")
        # 20 closest chords to 'C'
        vectors = []
        chord_names = []
        similar_chords = model.wv.similar_by_word('C', topn=20)
        for c in similar_chords:
            vectors.append(model.wv.get_vector(c[0]))
            chord_names.append(c[0])

        weights = np.array(vectors)


    # do T-SNE
    tsne = TSNE(n_components=2,
              random_state=42,
              perplexity=30,
              learning_rate='auto',
              init='pca',
              n_iter=2000
              )
    T = tsne.fit_transform(weights)

    # plot
    projected = pd.DataFrame(T)

    fig = px.scatter(
      projected,
      x=0, y=1,
      #color='mode',
      text=chord_names,
      width=800, height=600,
      title=f"T-SNE applied to Doc2Vec Weights, {preprocessing}"
    )
    fig.update_traces(textposition='top center')
    fig.update_traces(textfont_size=12, selector=dict(type='scatter'))
    fig.show()



def generate_webapp_data(doc2vecObj, preprocessing):
    df_webapp = doc2vecObj.get_tune_similarity()

    # save to file
    (df_webapp
     .loc[:, ['reference_title',
              'reference_titleid',
              'ref_sectionid',
              'ref_section_label',
              'similar_titleid',
              'similar_title',
              'similar_sectionid',
              'similar_section_label',
              'score'
              ]]
     .reset_index()
     .to_csv(f'output/model/recommender_{doc2vecObj.model_name}_{preprocessing}.csv', encoding='utf8', index=False)
     )

    with zipfile.ZipFile(f'output/model/recommender_{doc2vecObj.model_name}_{preprocessing}.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(f'output/model/recommender_{doc2vecObj.model_name}_{preprocessing}.csv')


if __name__ == "__main__":
    set_pandas_display_options()

    for p in ['rootAndDegreesPlus', 'rootAndDegreesSimplified']:
        print(f'*** Chord Preprocessing: {p} ***')
        # initialize model with the chords preprocessing method
        mod = CalculateDoc2VecModel(p)

        wandb = UseWandB(use=False, project_name='doc2vec_dbow1', data=mod, comment="")
        wandb.store_input_file(mod.input_file)

        if False:
            # Calculate the Model
            mod.calculate_doc2vec_model()
            mod.store_model()

        mod.load_model()

        diatonic_chords(mod, p)

        df = corpus_chord_ngram(mod, ngrams=[1,2,3,4])
        #plot_weights(mod, p)

        pairs = ['G7', 'C', 'C7', 'F']
        pairs = ['G', 'C', 'C', 'F']
        pairs = ['Am', 'C', 'Cm', 'Eb']

        sims = mod.doc2vec.wv.most_similar(positive=[pairs[1], pairs[2]], negative=[pairs[0]], topn=5)
        if sims[0][0] == pairs[3]:
            print(f"Found the analogy: {pairs[0]}-{pairs[1]} is like {pairs[2]}-{pairs[3]}")
        else:
            print(f"Did not find the analogy. Best matches are: {sims}")

        mod.doc2vec.wv.evaluate_word_analogies('chords_analogy.txt', case_insensitive=False)

        # Test
        #do_contrafacts_test(mod)

        # Generate full data for web application
        if True:
            generate_webapp_data(mod, p)
            wandb.store_artifacts(mod, p)

        # Done.
        wandb.finish()

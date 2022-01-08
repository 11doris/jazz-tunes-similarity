import pandas as pd
from dataset.utils import set_pandas_display_options
from model.CalculateDoc2VecModel import *
from model.UseWandB import *
import numpy as np
import zipfile


def calculate_model(doc2vecObject):
    # train the model on the train data
    doc2vecObject.calculate_doc2vec_model()

    # store the model and similarity matrix
    doc2vecObject.store_model()


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


def test_diatonic_chords(doc2vecObj):
    test_tokens = ['C',
                   'Dm',
                   'Em',
                   'F',
                   'G7',
                   'Am',
                   # 'Bm7b5',
                   'F7',
                   'D7',
                   'A7',
                   'E7',
                   'B7',
                   'F#7',
                   'Cm',
                   'D']

    model = doc2vecObj.doc2vec
    if 1 in preprocess_config['ngrams']:
        ref = 'C'
        print(f"Similarity for Chords relative to {ref}")
        for t in test_tokens:
            print(f"{model.wv.similarity(ref, t):.3f}: {ref} <-> {t}")

        print(f"\nMost similar to {ref}:")
        for t in model.wv.similar_by_word(ref, topn=20):
            print(t)


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


if __name__ == "__main__":
    set_pandas_display_options()

    for p in ['rootAndDegreesSimplified', 'rootAndDegreesPlus']:
        print(f'*** Chord Preprocessing: {p} ***')
        # initialize model with the chords preprocessing method
        mod = CalculateDoc2VecModel(p)

        run = 0
        for dbow_words in [0, 1]:
            for vector_size in [100, 200, 300, 400]:
                for window in [2, 3, 4]:
                    for negative in [2, 4, 8, 10, 12]:
                        for sample in [0.01, 0.05, 0.1, 0.2]:
                            for epochs in [30, 40, 50, 60]:
                                for repeat in [1, 2, 3, 4]:
                                    mod.model_config['model']['dbow_words'] = dbow_words
                                    mod.model_config['model']['vector_size'] = vector_size
                                    mod.model_config['model']['window'] = window
                                    mod.model_config['model']['negative'] = negative
                                    mod.model_config['model']['sample'] = sample
                                    mod.model_config['model']['epochs'] = epochs

                                    print()
                                    print('-'*80)
                                    print(f"{p}, Search run: {run}")
                                    print(f'dbow_words: {dbow_words}')
                                    print(f'vector_size: {vector_size}')
                                    print(f'window: {window}')
                                    print(f'negative: {negative}')
                                    print(f'sample: {sample}')
                                    print(f'epoch: {epochs}')
                                    print(f'repeat run: {repeat}')
                                    run +=1

                                    wandb = UseWandB(use=True, project_name='doc2vec', data=mod, comment="")
                                    wandb.store_input_file(mod.input_file)

                                    # Calculate the LSI Model
                                    calculate_model(mod)

                                    test_diatonic_chords(mod)
                                    #plot_weights(mod, p)

                                    # Test
                                    do_contrafacts_test(mod)

                                    # Done.
                                    wandb.finish()

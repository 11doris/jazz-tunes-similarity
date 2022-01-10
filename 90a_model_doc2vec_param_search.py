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

    wandb.store_result_contrafacts(doc2VecObject.model_name, matches, df_sim)


# Evaluate self-similarity of the sections
def do_self_similarity_test(doc2vecObj):
    counter, self_similar_prop = doc2vecObj.self_similarity_test()
    print(counter)
    print(f"Sections that are self-similar in first rank: {self_similar_prop[0]*100:.3f}%")
    print(f"Sections that are self-similar in first or second rank: {self_similar_prop[1]*100:.3f}%")
    print()

    wandb.store_result_self_similarity(self_similar_prop)

def similar_chords(doc2vecObj, preprocessing):

    model = doc2vecObj.doc2vec
    if 1 in preprocess_config['ngrams']:
        if preprocessing == 'rootAndDegreesPlus':
            ref = 'C'
        else:
            ref = 'CM7'

        print(f"\nMost similar to {ref}:")
        for t in model.wv.similar_by_word(ref, topn=20):
            print(t)


def do_chord_analogy_test(model):
    n = 5

    with open('chords_analogy2.txt') as f:
        lines = f.read().splitlines()

    pairs = [line.split(" ") for line in lines]
    perfect_match = 0
    topn_match = 0
    for pair in pairs:
        # print(f"{pair[0]}-{pair[1]} is like {pair[2]} to ?")
        sims = model.doc2vec.wv.most_similar(positive=[pair[1], pair[2]], negative=[pair[0]], topn=n)
        if sims[0][0] == pair[3]:
            print(f"Perfect: {pair[0]}-{pair[1]} is like {pair[2]}-{pair[3]}")
            perfect_match += 1
            topn_match += 1
        else:
            if pair[3] in [item[0] for item in sims]:
                print(f"Top {n}: {pair[0]}-{pair[1]} is like {pair[2]}-{pair[3]}")
                topn_match += 1

    prop_perfect = perfect_match / len(pairs)
    prop_topn = topn_match / len(pairs)
    print(f"Perfect matches: {100 * prop_perfect:.3}%")
    print(f"Top {n} matches: {100 * prop_topn:.3}%")
    wandb.store_result_chord_analogy([prop_perfect, prop_topn], n)


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

    for p in ['rootAndDegreesPlus', 'rootAndDegreesSimplified']:
        print(f'*** Chord Preprocessing: {p} ***')
        # initialize model with the chords preprocessing method
        mod = CalculateDoc2VecModel(p)

        run = 0
        for dbow_words in [1]:
            for sample in [0.005]:
                for vector_size in [300]:
                    for window in [2]:
                        for negative in [10]:
                            for epochs in [40]:
                                for min_count in [10]:
                                    for hs in [1]:
                                        for repeat in range(3):
                                            mod.model_config['dbow_words'] = dbow_words
                                            mod.model_config['vector_size'] = vector_size
                                            mod.model_config['window'] = window
                                            mod.model_config['negative'] = negative
                                            mod.model_config['sample'] = sample
                                            mod.model_config['epochs'] = epochs
                                            mod.model_config['min_count'] = min_count
                                            mod.model_config['hs'] = hs
                                            print()
                                            print('-'*80)
                                            print(mod.model_config)
                                            print()
                                            print(f"{p}, Search run: {run}")
                                            print(f'dbow_words: {dbow_words}')
                                            print(f'vector_size: {vector_size}')
                                            print(f'window: {window}')
                                            print(f'negative: {negative}')
                                            print(f'sample: {sample}')
                                            print(f'epoch: {epochs}')
                                            print(f'min_count: {min_count}')
                                            print(f'hs: {hs}')
                                            print(f'repeat run: {repeat}')
                                            run +=1

                                            wandb = UseWandB(use=True, project_name='doc2vec_dbow1', data=mod, comment="")
                                            wandb.store_input_file(mod.input_file)

                                            # Calculate the LSI Model
                                            calculate_model(mod)

                                            similar_chords(mod, p)
                                            #plot_weights(mod, p)

                                            # Test
                                            do_contrafacts_test(mod)
                                            do_chord_analogy_test(mod)

                                            if False:
                                                do_self_similarity_test(mod)

                                            # Done.
                                            wandb.finish()

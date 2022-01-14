import pandas as pd
from dataset.utils import set_pandas_display_options
from model.CalculateDoc2VecModel import *
from model.UseWandB import *
import zipfile
import collections
from tqdm import tqdm


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


def do_chord_analogy_test(model):
    n = 5

    with open('tests/fixtures/test_chord_analogies.txt') as f:
        lines = f.read().splitlines()

    pairs = [line.split(" ") for line in lines]
    perfect_match = 0
    topn_match = 0
    for pair in pairs:
        sims = model.doc2vec.wv.most_similar(positive=[pair[1], pair[2]], negative=[pair[0]], topn=n)
        if sims[0][0] == pair[3]:
            #print(f"Found:     {pair[0]}-{pair[1]} and {pair[2]}-{pair[3]}")
            perfect_match += 1
            topn_match += 1
        else:
            if pair[3] in [item[0] for item in sims]:
                #print(f"Top {n}:     {pair[0]}-{pair[1]} and {pair[2]}-{pair[3]}")
                topn_match += 1
            #else:
            #    print(f"Not found: {pair[0]}-{pair[1]} and {pair[2]}-{pair[3]}")

    prop_perfect = perfect_match / len(pairs)
    prop_topn = topn_match / len(pairs)
    print(f"Perfect matches: {100 * prop_perfect:.3}%")
    print(f"Top {n} matches: {100 * prop_topn:.3}%")
    wandb.store_result_chord_analogy([prop_perfect, prop_topn], n)


def similar_chords(doc2vecObj, preprocessing):
    model = doc2vecObj.doc2vec
    if 1 in preprocess_config['ngrams']:
        if preprocessing == 'rootAndDegreesPlus':
            ref = 'F'
        else:
            ref = 'FM7'

        print(f"\nMost similar to {ref}:")
        for t in model.wv.similar_by_word(ref, topn=20):
            print(t)


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

        wandb = UseWandB(use=True, project_name='model_comparison', data=mod, comment="")
        wandb.store_input_file(mod.input_file)

        if True:
            # Calculate the Model
            mod.calculate_doc2vec_model()
            mod.store_model()

        mod.load_model()

        # just as a visual cross-check, visualize similar chords
        similar_chords(mod, p)

        # Test
        do_contrafacts_test(mod)
		if True:
        	do_self_similarity_test(mod)

        if p == 'rootAndDegreesPlus':
            do_chord_analogy_test(mod)

        # Generate full data for web application
        if True:
            generate_webapp_data(mod, p)
            wandb.store_artifacts(mod, p)

        # Done.
        wandb.finish()

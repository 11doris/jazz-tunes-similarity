import pandas as pd
from dataset.utils import set_pandas_display_options
from model.CalculateLsiModel import *
from model.UseWandB import *
import numpy as np
import zipfile


def calculate_model(lsiObject):
    # train the model on the train data
    lsiObject.calculate_lsi_model()

    # get the LSI topics for each tune
    df_vectors = lsiObject.get_train_tune_vectors()
    # make sure there are no nan or inf values in the weights
    invalid = df_vectors[df_vectors.isin([np.nan, np.inf, -np.inf]).any(1)]
    assert(len(invalid) == 0)

    # store the model and similarity matrix
    lsiObject.store_model()
    lsiObject.store_similarity_matrix()


def do_contrafacts_test(lsiObject):
    # test how many of the contrafacts are found
    matches, results = lsiObject.lsi_test_contrafacts()

    for rr, val in results.items():
        if val == 0:
            print(f"{val}: {rr}")

    df_sim = pd.DataFrame.from_dict(results, orient='index')
    df_sim = df_sim.reset_index()
    df_sim.sort_values('index')
    print(df_sim)
    print()
    print(f"Found matches: {matches} out of {len(results)}: {100 * matches / len(results):.3f}%")

    wandb.store_result_contrafacts('lsi', matches, df_sim)


def generate_webapp_data(lsiObject, filename):
    df_webapp = lsiObject.get_tune_similarity()

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
     .to_csv(f'{filename}.csv', encoding='utf8', index=False)
     )

    with zipfile.ZipFile(f'{filename}.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(f'{filename}.csv')


if __name__ == "__main__":
    set_pandas_display_options()

    for runs in range(1):
        for p in ['chordsBasic', 'chordsSimplified']:
            for ngram in [[1,2], [1,2,3]]:

                # initialize model with the chords preprocessing method
                mod = CalculateLsiModel(p, ngram)

                wandb = UseWandB(use=True, project_name='model_comparison', data=mod, comment="")
                wandb.store_input_file(mod.input_file)

                # Calculate the LSI Model
                calculate_model(mod)

                # Store vocab size and number of total terms to wandb
                wandb.store_result_vocab(mod.get_vocab_info())

                # Test
                do_contrafacts_test(mod)

                # Generate full data for web application
                if True:
                    f = f'output/model/recommender_{mod.model_name}_{p}_{mod.get_ngrams_as_str()}'
                    generate_webapp_data(mod, filename=f)
                    wandb.store_artifacts(mod, p, recommender_filename=f)

                # Done.
                wandb.finish()

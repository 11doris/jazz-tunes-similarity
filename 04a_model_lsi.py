import pandas as pd
from dataset.utils import set_pandas_display_options
from model.CalculateLsiModel import *
from model.UseWandB import *
import numpy as np
import zipfile


if __name__ == "__main__":
    set_pandas_display_options()
    preprocessing = 'rootAndDegreesPlus'
    prep = CalculateLsiModel(preprocessing)

    print(f'Test Corpus: {len(prep.get_test_corpus())} sections')
    print(f'Train Corpus: {len(prep.get_train_corpus())} sections')
    print()

    wandb = UseWandB(use=False, project_name='lsi_model', data=prep, comment="")
    wandb.store_input_file(prep.input_file)

    ## Calculate the LSI Model

    # train the model on the train data
    prep.calculate_lsi_model()
    # after training, add the test data to the model for later querying
    prep.add_test_documents_to_model()

    # get the LSI topics for each tune
    df_vectors = prep.get_train_tune_vectors()
    # make sure there are no nan or inf values in the weights
    invalid = df_vectors[df_vectors.isin([np.nan, np.inf, -np.inf]).any(1)]
    assert(len(invalid) == 0)

    # store the model and similarity matrix
    prep.store_model()
    prep.store_similarity_matrix()

    ## Test

    # test how many of the contrafacts are found
    matches, results = prep.lsi_test_contrafacts()

    for rr, val in results.items():
        if val == 0:
            print(f"{val}: {rr}")

    df_sim = pd.DataFrame.from_dict(results, orient='index')
    df_sim = df_sim.reset_index()
    df_sim.sort_values('index')
    print(df_sim)
    print()
    print(f"Found matches: {matches} out of {len(results)}: {100 * matches / len(results):.3f}%")

    wandb.store_results(matches, df_sim)


    ## Generate full data for web application

    if False:
        df_webapp = prep.get_sim_scores()

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
         .to_csv(f'output/model/recommender_lsi_{preprocessing}.csv', encoding='utf8', index=False)
         )

        with zipfile.ZipFile(f'output/model/recommender_lsi_{preprocessing}.zip', 'w') as zf:
            zf.write(f'output/model/recommender_lsi_{preprocessing}.csv')

    wandb.store_artifacts(preprocessing)

    wandb.finish()

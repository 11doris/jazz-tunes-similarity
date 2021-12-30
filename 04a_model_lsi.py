import pandas as pd
from dataset.utils import set_pandas_display_options
from model.CalculateLsiModel import *
from model.UseWandB import *
import zipfile


if __name__ == "__main__":
    set_pandas_display_options()
    prep = CalculateLsiModel('rootAndDegreesPlus')

    print(prep.sectionid_to_title(1370))

    wandb = UseWandB(use=False, project_name='test_code', data=prep)
    wandb.store_input_file(prep.input_file)

    prep.corpus()

    print(f'Full Corpus: {len(prep.get_processed_corpus())} sections')
    print(f'Test Corpus: {len(prep.get_test_corpus())} sections')
    print()

    prep.calculate_lsi_model()
    prep.store_similarity_matrix()

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

    # CONTINUE HERE
    df_sim = prep.get_sim_scores(topn=30)

    # save to file
    (df_sim
     .loc[:, [  # 'reference_title',
                 'reference_titleid',
                 # 'similar_title',
                 'similar_titleid',
                 'ref_section_label',
                 'similar_section_label',
                 'score'
             ]]
     .groupby(['reference_titleid',
               # 'reference_title',
               'similar_titleid',
               # 'similar_title',
               'ref_section_label',
               'similar_section_label'])
     .max('score')
     .reset_index()
     .to_csv(f'output/model/recommender_lsi.csv', encoding='utf8', index=False)
     )

    with zipfile.ZipFile(f'output/recommender_lsi.zip', 'w') as zf:
        zf.write(f'output/recommender_lsi.csv')


    wandb.store_results(matches, df_sim)

    wandb.finish()
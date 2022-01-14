import pandas as pd
from dataset.utils import set_pandas_display_options
import matplotlib.pyplot as plt
import zipfile


if __name__ == "__main__":

    set_pandas_display_options()

    # define here from which model the results of the two different chord preprocessing strategies should be unified.
    model = 'lsi'

    input_files = [
        f'output/model/recommender_{model}_chordsBasic.zip',
        f'output/model/recommender_{model}_rootAndDegreesSimplified.zip'
    ]

    df_list = []
    for f in input_files:
        temp_df = pd.read_csv(f)
        temp_df['method'] = "Basic" if "Plus" in f.split('/')[-1].split('.')[0] else "Simplified"
        df_list.append(temp_df)

    df_list

    ref_titles = (df_list[0]
                  .loc[:, ['reference_titleid', 'ref_section_label']]
                  .drop_duplicates()
                  )

    # find the common tunes for all recommendation methods

    len_common = []

    dict_comparison = {
        'titleid': [],
        'section_label': [],
        'common': [],
        'unique_simp': [],
        'unique_plus': [],
    }

    common = (df_list[0]
              .merge(df_list[1], on=['reference_title',
                                     'reference_titleid',
                                     'ref_section_label',
                                     'ref_sectionid',
                                     'similar_titleid',
                                     'similar_title',
                                     'similar_sectionid',
                                     'similar_section_label'])
              )
    common['common'] = True
    common['score'] = common[['score_x', 'score_y']].max(axis=1)
    common['method'] = 'Both'

    common.drop(['score_x', 'score_y', 'method_x', 'method_y', 'index_x', 'index_y'], inplace=True, axis=1)

    unique = (df_list[0]
              .merge(df_list[1], on=['reference_title',
                                     'reference_titleid',
                                     'ref_section_label',
                                     'ref_sectionid',
                                     'similar_titleid',
                                     'similar_title',
                                     'similar_sectionid',
                                     'similar_section_label'], how='outer', indicator=True)
              .query('_merge != "both"')
              .drop(columns=['_merge'])
              )

    unique['score_x'].fillna(0.0, inplace=True)
    unique['score_y'].fillna(0.0, inplace=True)
    unique['method_x'].fillna("", inplace=True)
    unique['method_y'].fillna("", inplace=True)
    unique['score'] = unique['score_x'] + unique['score_y']
    unique['method'] = unique['method_x'] + unique['method_y']
    unique.drop(['score_x', 'score_y', 'method_x', 'method_y', 'index_x', 'index_y'], inplace=True, axis=1)
    unique = unique.sort_values(['ref_sectionid', 'score'], ascending=[True, False])
    unique['common'] = False

    df = pd.concat([common, unique])
    df = df.sort_values(['ref_sectionid', 'common', 'score'], ascending=[True, False, False])
    df['method'] = df['method'].str.replace('recommender_lsi_simp', 'simplified')
    df['method'] = df['method'].str.replace('recommender_lsi_plus', 'basic')

    common_count = common.value_counts(['reference_titleid', 'ref_section_label'])
    unique_count = unique.value_counts(['reference_titleid', 'ref_section_label'])

    ax1 = plt.subplot(1, 2, 1)
    plt.hist(common_count, bins=15)
    ax1.set_title(f'Common for {model}')

    ax2 = plt.subplot(1, 2, 2, sharex=ax1)
    plt.hist(unique_count, bins=15)
    ax2.set_title(f'Unique for {model}')

    plt.show()

    f = 'output/model/unified_model_result'
    # reference_titleid, similar_titleid, ref_section_label, similar_section_label, score
    (df[['reference_titleid',
         'similar_titleid',
         'ref_section_label',
         'similar_section_label',
         'method',
         'score']]
     .to_csv(f"{f}.csv")
     )
    with zipfile.ZipFile(f"{f}.zip", 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(f"{f}.csv")

    print(f"Output data for webapp is stored to: {f}.zip.")

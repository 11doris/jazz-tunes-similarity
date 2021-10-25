import pandas as pd
import numpy as np
from dataset.utils import set_pandas_display_options

if __name__ == "__main__":
    set_pandas_display_options()

    # load the data from the previous steps
    df_brainz = pd.read_csv('02b_tunes_musicbrainz.csv', sep='\t', encoding='utf8')
    df_brainz = df_brainz.drop(['title', 'composer'], axis=1)
    df_transform = pd.read_csv('02_tunes_raw.csv', sep='\t', encoding='utf8', index_col="id")

    # merge the two sources together
    df = df_transform.merge(df_brainz, on='file_name')
    assert(len(df_transform) == len(df))

    # if musicbrainz found no composer, use the information from iRealPro
    df.rename(columns={'composer': 'ireal_composer'}, inplace=True)
    df['composer_tmp'] = np.where(df['musicbrainz_composer'] == '[]', df['ireal_composer'], df['musicbrainz_composer'])
    df['composer'] = df['composer_tmp'].str.strip('][').str.strip("'").str.split("', '")

    df = df.explode('composer')
    df = df.drop(['ireal_composer', 'composer_tmp'], axis=1)

    print(df.columns)
    df.to_csv('02c_tune_composers.csv', sep='\t', header=True, index_label='id')
    df['lyricist'] = df['musicbrainz_lyricist'].apply(lambda x: x[1:-1]).str.replace("'", "").str.strip("][")

    dd = df.loc[:, ['file_name',
                    'title',
                    'composer',
                    'year',
                    'year_truncated',
                    'tonality',
                    'tune_key',
                    'tune_mode',
                    'structure',
                    'num_bars',
                    'time_signature',
                    'cycle_fifths_order',
                    'style',
                    'musicbrainz_id',
                    'wikidata_id',
                    'wikidata_allmusic',
                    'wiki_link',
                    'wikidata_description',
                    'lyricist',
                    ]]

    dd.to_csv('02c_tune_sql_import.csv', sep='\t', header=True, encoding='utf8', index_label='id')

    print(f"{len(df_transform)} tunes")
    print(f"{len(df)} rows with composers exploded")


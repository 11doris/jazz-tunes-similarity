import pandas as pd
import numpy as np
from dataset.utils import set_pandas_display_options

if __name__ == "__main__":
    set_pandas_display_options()

    df = pd.read_csv('02b_tunes_musicbrainz.csv', sep='\t', index_col="id")

    # TODO temp remove this, it's in 02_transform
    df['time_signature'] = df['beats'].astype('int').astype('str') + "/" + df['beat_time'].astype('int').astype('str')


    # if musicbrainz found no composer, use the information from iRealPro
    df.rename(columns={'composer': 'ireal_composer'}, inplace=True)
    df['composer_tmp'] = np.where(df['musicbrainz_composer'] == '[]', df['ireal_composer'], df['musicbrainz_composer'])
    df['composer'] = df['composer_tmp'].str.strip('][').str.strip("'").str.split("', '")

    df = df.explode('composer')
    df = df.drop(['ireal_composer', 'composer_tmp'], axis=1)

    print(df.columns)
    df.to_csv('02c_tune_composers.csv', sep=',', header=True, index_label='Id')

    dd = df.loc[:, ['path_name',
                    'title',
                    'composer',
                    'year',
                    'tonality',
                    'tune_key',
                    'tune_mode',
                    'structure',
                    'num_bars',
                    'time_signature',
                    'cycle_fifths_order',
                    'style',
                    ]]

    dd.to_csv('02c_tune_sql_import.csv', sep=',', header=True, index_label='Id')

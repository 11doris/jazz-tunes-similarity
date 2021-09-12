import os
import json
import pandas as pd


##
# read meta info and convert to data frame
meta = json.load(open('../../dataset/meta_info.json'))
df = pd.DataFrame.from_dict(meta, orient='index')
df.reset_index(inplace=True)
df = df.rename(columns = {'index': 'file_name'})

##
#

print(f'Found {len(df)} files to parse... ')


## Split multiple composers to multiple rows
#
df = df.assign(composer=df.composer.str.split(',')).explode('composer')
df = df.assign(composer=df.composer.str.split('-')).explode('composer')
df['composer'] = df['composer'].str.strip()

##
#
composer_tunes = df.groupby('composer').title.count().sort_values(ascending=False)
composer_tunes.head(50)


##
#
df.reset_index(inplace=True)
df.to_csv('ireal_composer_separated.csv', sep='\t', index=False)


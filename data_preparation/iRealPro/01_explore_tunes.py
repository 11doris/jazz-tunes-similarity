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

df.groupby('composer').count()

##
# Cleaning

# If the year is contained in the composer column, extract it to a new column
df['year'] = df['composer'].str.extract(r"\(?(18[0-9]{2}|19[0-9]{2}|20[0-9]{2})\)?")

# write data frame with filename and year to disk
df_year = df[['file_name', 'title', 'composer', 'year']]
df_year.to_csv('ireal_year.csv', sep='\t', index=False)


#
df['composer'] = df['composer'].str.replace(r"\(?(18[0-9]{2}|19[0-9]{2}|20[0-9]{2})\)?", "", regex=True).str.strip()

# Remove the (Dixieland Tunes) from the title
df['title'] = df['title'].str.replace("(Dixieland Tunes)", "", regex=False).str.strip()
df['title'] = df['title'].str.replace("(dixieland Tunes)", "", regex=False).str.strip()

# Fix composer names
df['composer'] = df['composer'].str.replace("Van-Heusen", "Van Heusen", regex=False)
df['composer'] = df['composer'].str.replace("Armstroong", "Louis Armstrong", regex=False)
df['composer'] = df['composer'].str.replace("Antonio-Carlos", "Antonio Carlos", regex=False)


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


import pandas as pd
from dataset.utils import set_pandas_display_options


if __name__ == "__main__":
    set_pandas_display_options()

    df = pd.read_csv('02b_tunes_musicbrainz_full.csv', sep='\t', index_col="id")

    ##
    # create a column which indicates whether there is a year mismatch between what we gathered so far and Wikidata
    #
    df['wikidata_year'] = df['wikidata_year'].str[0:4]
    df['wikidata_year'] = df['wikidata_year'].astype('float')

    df['year_mismatch'] = (df['year'].notna()) & (df['wikidata_year'].notna()) & (df['year'] != df['wikidata_year'])

    dd = df.loc[:, ['file_name', 'year', 'wikidata_year', 'year_mismatch']]
    print(f"Number of mismatch years: {dd['year_mismatch'].value_counts()}")

    print(dd.head(15))

    # Write resulting data frame to file
    dd.to_csv('02c_years_mismatch.csv', sep='\t', encoding='utf8', index=False)

    ##
    # create a column which indicates whether there is a key mismatch between iRealPro and Wikidata
    #
    df['key_irealpro'] = df['key'].str.strip() + " " + df['mode'].str.strip()

    dd = df.loc[:, ['file_name', 'key_irealpro', 'wikidata_tonality']]
    dd['wikidata_tonality'] = dd['wikidata_tonality'].str.replace('-flat', 'b')
    dd['key_mismatch'] = (dd['key_irealpro'].notna()) & (dd['wikidata_tonality'].notna()) & (dd['key_irealpro'] != dd['wikidata_tonality'])

    # Write resulting data frame to file
    dd.to_csv('02c_keys_mismatch.csv', sep='\t', encoding='utf8', index=False)

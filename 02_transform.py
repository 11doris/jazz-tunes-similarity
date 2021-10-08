import pandas as pd
import numpy as np
from dataset.readData import ReadData
from dataset.utils import set_pandas_display_options
from chords.symbol.parts.noteSymbol import Note


def read_realbook_data():
    realbook = pd.read_csv('./data_preparation/real_books/songlist_year.csv', sep=',', quotechar='|')
    realbook = realbook[['title', 'file_name', 'year']]
    realbook = realbook.drop_duplicates()

    return realbook

def read_manual_years_data():
    df = pd.read_csv('./data_preparation/irealpro_manual_year.csv', sep='\t', quotechar='|')
    df = df[['title', 'file_name', 'year']]
    df = df.drop_duplicates()

    return df

def add_title_simplified(df):
    stop = ['a', 'the']

    # remove articles, everything in round brackets, punctuation
    df['title_simplified'] = df['title'].str.lower().apply(
        lambda x: ''.join([word for word in x.split() if word not in (stop)]))
    df['title_simplified'] = df['title_simplified'].str.replace('\(.*\)', '', regex=True)
    df['title_simplified'] = df['title_simplified'].str.replace('-', '', regex=True)
    df['title_simplified'] = df['title_simplified'].str.replace('[^\w\s]', '', regex=True).str.strip()
    df['title_simplified'] = df['title_simplified'].str.replace('\s', '', regex=True).str.strip()

    return df


def manual_title_cleaning(df):
    # manual title adaptions to match with realbook
    titles = [
        ['allofsuddenmyheartsings', 'myheartsings'],
        ['mamboinn', 'atmamboinn'],
        ['youbetterleaveitalone', 'betterleaveitalone'],
        ['manhadecarnaval', 'blackorpheus'],
        ['bouncinwithbud', 'bouncingwithbud'],
        ['besamemucho', 'bésamemucho'],
        ['cantaloupeisland', 'canteloupeisland'],
        ['crazyhecallsme', 'crazyshecallsme'],
        ['donothintilyouhearfromme', 'donothintillyouhearfromme'],
        ['doyouknowwhatitmeans', 'doyouknowwhatitmeanstomissneworleans'],
        ['everythingilove', 'evrythingilove'],
        ['freighttrain', 'freighttrane'],
        ['frenesi', 'frenesí'],
        ['heebiejeebies1', 'heebiejeebies'],
        ['cantgetstarted', 'cantgetstartedwithyou'],
        ['ghostofchance', 'idontstandghostofchance'],
        ['igetalongwithoutyou', 'igetalongwithoutyouverywell'],
        ['igotitbad', 'igotitbadandthataintgood'],
        ['ivetoldeverylittlestar', 'ivetoldevrylittlestar'],
        ['untilrealthingcomesalong', 'itwillhavetodountilrealthingcomesalong'],
        ['justasittinandarockin', 'justsettinandrockin'],
        ['longagoandfaraway', 'longago'],
        ['nancy', 'nancywithlaughingface'],
        ['corcovado', 'quietnightsofquietstars'],
        ['stjamesinfirmary', 'saintjamesinfirmary'],
        ['taketrain', 'takeatrain'],
        ['bestthingforyouisme', 'bestthingforyou'],
        ['swingingshepherdblues', 'swinginshepherdblues'],
        ['allworldiswaitingforsunrise', 'worldiswaitingforsunrise'],
        ['moonlightsavingtime', 'moonlightsavingstime'],
        ['thiscouldbestartofsomethinggood', 'thiscouldbestartofsomethingbig'],
        ['toottoottootsiegoodbye', 'toottoottootsie'],
        ['questionandanswer', 'questionanswer'],
        ['whatdifferencedaymade', 'whatdiffrencedaymade'],
        ['youbroughtnewkindoflove', 'youbroughtnewkindoflovetome'],
        ['yourenobodytillsomebodylovesyou', 'yourenobodytilsomebodylovesyou'],
        ['aguadebeber', 'águadebeber'],
    ]
    for _from, _to in titles:
        df['title_simplified'] = df['title_simplified'].str.replace(_from, _to, regex=False)

    return df

def merge_year_from_manual_list(df) -> pd.DataFrame:
    original_order = list(df.columns)

    manual = read_manual_years_data()
    manual = add_title_simplified(manual)
    df = add_title_simplified(df)

    # full outer join on the simplified title to match the tunes from the Real Books with the iRealPro tunes
    join_df = pd.merge(manual, df, on='title_simplified', how='outer')
    # If the year from the manually curated list is available, take this, otherwise take the year from iRealPro
    join_df['year'] = np.where(join_df['year_x'].isna() == False, join_df['year_x'], join_df['year_y'])

    # Print summary
    na_per_col = join_df.dropna(subset=['title_y']).isna().sum()
    print(f'Total number of tunes: {len(join_df)}')
    print(f'Number of missing years for iReal: {na_per_col["year"]}')

    # cleanup unused columns
    join_df.rename(columns={'title_y': 'title',
                            'file_name_y': 'file_name'}, inplace=True)
    join_df = join_df.drop(columns=['title_x', 'year_x', 'year_y', 'title_simplified', 'file_name_x'])

    # sort the dataframe and drop the numbered index
    join_df = join_df.sort_values('file_name').reset_index(drop=True)

    # restore the original order of the data frame
    join_df = join_df[original_order]

    return join_df



def merge_year_from_realbook(df) -> pd.DataFrame:
    original_order = list(df.columns)

    # add column with a simplified and stemmed title for easier matching of the two data sets
    df = add_title_simplified(df)
    df = manual_title_cleaning(df)
    print(f'JSON meta input with missing years: {df.year.isnull().sum()}')

    # get the year information from RealBook and add simplified title
    realbook = read_realbook_data()
    realbook = add_title_simplified(realbook)
    realbook = realbook[['title', 'title_simplified', 'year']]

    # full outer join on the simplified title to match the tunes from the Real Books with the iRealPro tunes
    join_df = pd.merge(realbook, df, on='title_simplified', how='outer')
    # If the year from RealBooks is available, take this, otherwise take the year from iRealPro
    join_df['year'] = np.where(join_df['year_x'].isna() == False, join_df['year_x'], join_df['year_y'])

    #
    # Print summary
    num_common = len(join_df[['title_x', 'title_y']].dropna())
    num_ireal_only = join_df['title_x'].isna().sum()
    num_realbook_only = join_df['title_y'].isna().sum()
    na_per_col = join_df.dropna(subset=['title_y']).isna().sum()
    print(f'Total number of tunes: {len(join_df)}')
    print(f'Number of tunes common in realbook and ireal: {num_common}')
    print(f'Number of tunes only in ireal: {num_ireal_only}')
    print(f'Number of tunes only in realbook: {num_realbook_only}')
    print(f'Number of chord sequences: common + ireal: {num_common + num_ireal_only}')
    print(f'Number of missing years for iReal: {na_per_col["year"]}')

    # cleanup unused columns
    join_df = join_df.drop(columns=['title_x', 'year_x', 'year_y', 'title_simplified'])
    join_df.rename(columns={'title_y': 'title'}, inplace=True)

    # sort the dataframe and drop the numbered index
    join_df = join_df.sort_values('file_name').reset_index(drop=True)

    # drop all rows which have an empty value in 'file_name'; these are rows that were in RealBook but not in iRealPro
    join_df = join_df.dropna(subset=['file_name'])

    # restore the original order of the data frame
    join_df = join_df[original_order]

    return join_df


def key_to_cycle_of_fifths_order(x):
    fifths_major = [3, -2, 5, 0, -5, 2, -3, 4, -1, -6, 1, -4]
    fifths_minor = [0, -5, 2, -3, 4, -1, -6, 1, -4, 3, -2, 5]

    if x['mode'] == 'minor':
        return fifths_minor[x['key']]
    elif x['mode'] == 'major':
        return fifths_major[x['key']]
    else:
        print("weird mode!!: " + x['mode'])


if __name__ == "__main__":
    set_pandas_display_options()

    read_obj = ReadData()

    df = pd.read_json(read_obj.meta_path, orient='index')
    df.reset_index(inplace=True)
    df = df.rename(columns={'index': 'file_name'})

    df = pd.concat([df, df["default_key"].apply(pd.Series)], axis=1)
    df = pd.concat([df, df["time_signature"].apply(pd.Series)], axis=1)
    df = df.drop(columns=["default_key", "time_signature"])

    df['cycle_fifths_order'] = df.apply(key_to_cycle_of_fifths_order, axis=1)

    # transform key number to note name
    df['key'] = df['key'].apply(lambda x: Note(x).toSymbol())

    # get and merge the publishing year information from the realbook csv
    df = merge_year_from_realbook(df)

    # get and merge the manually curated list of publishing years
    df = merge_year_from_manual_list(df)

    print(df.columns)
    print(df.head(50))

    # save data frame to disk
    df.to_csv('tunes.csv', sep='\t')
    print(df.columns)
    df.rename(columns={'file_name': 'path_name',
                         'key': 'tune_key',
                         'mode': 'tune_mode'}, inplace=True)


    # save a simplified table to disk for trials with mySQL
    dd = df.loc[:, ['path_name', 'composer', 'style', 'num_bars', 'title', 'year', 'tune_key', 'tune_mode']]
    dd['year'].fillna(0, inplace=True)
    dd.to_csv('tune_sql_import.csv', sep=',', header=True, index_label='Id')

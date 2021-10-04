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

def merge_year_from_realbook(df):
    original_order = list(df.columns)

    # add column with a simplified and stemmed title for easier matching of the two data sets
    df = add_title_simplified(df)
    df = manual_title_cleaning(df)

    # get the year information from RealBook and add simplified title
    realbook = read_realbook_data()
    realbook = add_title_simplified(realbook)
    realbook = realbook[['title_simplified', 'year']]

    # full outer join on the simplified title to match the tunes from the Real Books with the iRealPro tunes
    join_df = pd.merge(realbook, df, on='title_simplified', how='outer')
    # If the year from RealBooks is available, take this, otherwise take the year from iRealPro
    join_df['year'] = np.where(join_df['year_x'].isna() == False, join_df['year_x'], join_df['year_y'])

    # cleanup unused columns
    join_df = join_df.drop(columns=['year_x', 'year_y', 'title_simplified'])

    # sort the dataframe and drop the numbered index
    join_df = join_df.sort_values('file_name').reset_index()
    join_df = join_df.drop('index', axis=1)

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



    print(df.columns)
    print(df.head())

    # save data frame to disk
    df.to_csv('tunes.csv', sep='\t')


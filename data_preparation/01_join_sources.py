import pandas as pd
import numpy as np
import json

if __name__ == "__main__":
    """
    This helper creates a list of all tunes combined from the Real Books Vol 1-3 and iRealPro, including the file paths.
    The Real Books files are pdf files and used as the reference - the chord sequences are not available in digital 
    format, but the publishing year has been retrieved for all of these tunes and is considered as the reference.
    The iRealPro files are musicXML files and contain the chord sequences. 
    
    Read the list with the tunes from Real Books Vol 1-3, read list with tunes from iRealPro.
    Simplify the titles for easier matching, adapt titles manually where needed, and join the lists together.
    Use the Publishing Year information from RealBooks where available, Publishing Year information from iRealPro where 
    no RealBook information is available, leave empty if unknown.
    Write the result to disk.
    """

    # read meta info and convert to data frame
    meta = json.load(open('../dataset/meta_info.json'))
    df = pd.DataFrame.from_dict(meta, orient='index')
    df.reset_index(inplace=True)
    df_irealpro_raw = df.rename(columns={'index': 'file_name'})

    df_realbook_raw = pd.read_csv('./real_books/songlist_year.csv', sep=',', quotechar='|')
    df_realbook_raw.reset_index(inplace=True)


    ##
    # create data frame with file name, title, year and composer columns
    df_irealpro = df_irealpro_raw[['title', 'file_name', 'year', 'composer']]
    df_irealpro = df_irealpro.drop_duplicates()

    df_realbook = df_realbook_raw[['title', 'file_name', 'year']]
    df_realbook = df_realbook.drop_duplicates()


    # define a list of words to be removed
    stop = ['a', 'the']

    # remove articles, everything in round brackets, punctuation
    df_realbook['title_simplified'] = df_realbook['title'].str.lower().apply(lambda x: ''.join([word for word in x.split() if word not in (stop)]))
    df_realbook['title_simplified'] = df_realbook['title_simplified'].str.replace('\(.*\)','', regex=True)
    df_realbook['title_simplified'] = df_realbook['title_simplified'].str.replace('-','', regex=True)
    df_realbook['title_simplified'] = df_realbook['title_simplified'].str.replace('[^\w\s]','', regex=True).str.strip()
    df_realbook['title_simplified'] = df_realbook['title_simplified'].str.replace('\s','', regex=True).str.strip()

    # remove articles, everything in round brackets, punctuation
    df_irealpro['title_simplified'] = df_irealpro['title'].str.lower().apply(lambda x: ''.join([word for word in x.split() if word not in (stop)]))
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('\(.*\)','', regex=True)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('-','', regex=True)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('[^\w\s]','', regex=True).str.strip()
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('\s','', regex=True).str.strip()

    # manual title adaptions to match with realbook
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('allofsuddenmyheartsings','myheartsings', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('mamboinn','atmamboinn', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('youbetterleaveitalone','betterleaveitalone', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('manhadecarnaval','blackorpheus', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('bouncinwithbud','bouncingwithbud', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('besamemucho','bésamemucho', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('cantaloupeisland','canteloupeisland', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('crazyhecallsme','crazyshecallsme', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('donothintilyouhearfromme','donothintillyouhearfromme', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('doyouknowwhatitmeans','doyouknowwhatitmeanstomissneworleans', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('everythingilove','evrythingilove', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('freighttrain','freighttrane', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('frenesi','frenesí', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('heebiejeebies1','heebiejeebies', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('cantgetstarted','cantgetstartedwithyou', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('ghostofchance','idontstandghostofchance', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('igetalongwithoutyou','igetalongwithoutyouverywell', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('igotitbad','igotitbadandthataintgood', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('ivetoldeverylittlestar','ivetoldevrylittlestar', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('untilrealthingcomesalong','itwillhavetodountilrealthingcomesalong', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('justasittinandarockin','justsettinandrockin', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('longagoandfaraway','longago', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('nancy','nancywithlaughingface', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('corcovado','quietnightsofquietstars', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('stjamesinfirmary','saintjamesinfirmary', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('taketrain','takeatrain', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('bestthingforyouisme','bestthingforyou', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('swingingshepherdblues','swinginshepherdblues', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('allworldiswaitingforsunrise','worldiswaitingforsunrise', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('moonlightsavingtime','moonlightsavingstime', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('thiscouldbestartofsomethinggood','thiscouldbestartofsomethingbig', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('toottoottootsiegoodbye','toottoottootsie', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('questionandanswer','questionanswer', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('whatdifferencedaymade','whatdiffrencedaymade', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('youbroughtnewkindoflove','youbroughtnewkindoflovetome', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('yourenobodytillsomebodylovesyou','yourenobodytilsomebodylovesyou', regex=False)
    df_irealpro['title_simplified'] = df_irealpro['title_simplified'].str.replace('aguadebeber','águadebeber', regex=False)


    print(df_irealpro.head(50))

    ##
    # full outer join on the simplified title to match the tunes from the Real Books with the iRealPro tunes
    outer_join_df = pd.merge(df_realbook, df_irealpro, on='title_simplified', how='outer')
    outer_join_df['year'] = np.where(outer_join_df['year_x'].isna() == False, outer_join_df['year_x'], outer_join_df['year_y'])

    ##
    # Print summary
    num_common = len(outer_join_df[['title_x', 'title_y']].dropna())
    num_ireal_only = outer_join_df['title_x'].isna().sum()
    num_realbook_only = outer_join_df['title_y'].isna().sum()

    na_per_col = outer_join_df.dropna(subset=['title_y']).isna().sum()

    print(f'Total number of tunes: {len(outer_join_df)}')
    print(f'Number of tunes common in realbook and ireal: {num_common}')
    print(f'Number of tunes only in ireal: {num_ireal_only}')
    print(f'Number of tunes only in realbook: {num_realbook_only}')
    print(f'Number of chord sequences: common + ireal: {num_common + num_ireal_only}')
    print(f'Number of missing years for iReal: {na_per_col["year"]}')

    ##
    # Cleanup and save all tunes to csv
    df_year = outer_join_df[['file_name_y', 'title_y', 'composer', 'year']]
    df_year.columns = ['file_name', 'title', 'composer', 'year']
    df_year = df_year.dropna(subset=['file_name'])
    df_year.to_csv('tunes_year.csv', sep='\t', index_label='index')

    ##
    # Define data frame with all iRealPro tunes that still have a missing year
    df_miss = outer_join_df[['file_name_y', 'title_y', 'composer', 'year']]
    df_miss.columns = ['file_name', 'title', 'composer', 'year']
    df_miss = df_miss.dropna(subset=['title'])
    df_miss = df_miss[df_miss['year'].isna()]

    df_miss.to_csv('tunes_missing_year_generated-file.csv', sep='\t', index_label='index')


    ##
    # Update the meta.json file with the year information
    year_source_1 = pd.read_csv('tunes_year.csv', sep='\t', encoding='utf8')
    year_source_2 = pd.read_csv('irealpro_manual_year.csv', sep='\t', encoding='utf8')

    for index, row in year_source_1.iterrows():
        _year = row['year']
        if np.isnan(_year):
            meta[row['file_name']]['year'] = None
        else:
            meta[row['file_name']]['year'] = int(_year)

    for index, row in year_source_2.iterrows():
        _year = row['year']
        if np.isnan(_year):
            meta[row['file_name']]['year'] = None
        else:
            meta[row['file_name']]['year'] = int(_year)

    f = open("../dataset/meta_info.json", "w")
    f.write(json.dumps(meta, indent=2))
    f.close()

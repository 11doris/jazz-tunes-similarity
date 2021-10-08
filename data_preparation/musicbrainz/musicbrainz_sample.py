import musicbrainzngs
import pandas as pd
import re
from  dataset.utils import set_pandas_display_options


# don't cut the display of data frames for debugging reasons
set_pandas_display_options()


# Tell musicbrainz what your app is, and how to contact you
# (this step is required, as per the webservice access rules
# at http://wiki.musicbrainz.org/XML_Web_Service/Rate_Limiting )
musicbrainzngs.set_useragent("Jazz Maestro", "0.1", "http://example.com/music")

# If you are connecting to a different server
#musicbrainzngs.set_hostname("beta.musicbrainz.org")

# read in the CSV file with the
df = pd.read_csv('../tunes_year.csv', sep='\t', encoding='utf8')

df['composer_musicbrainz'] = ""
df['lyricist_musicbrainz'] = ""


for index, row in df.iterrows():
    print("*** " + row['title'] + " ***")
    if row['composer'] != 'nan':
        composers = re.split(' |, |,|-', row['composer'])
        composers = [composer.lower().strip() for composer in composers]
        # remove all elements with 2 or less characters
        composers = [i for i in composers if len(i) > 2]
    else:
        composers = []

    print(f"\t searching for {composers}")
    composer_set = set()
    lyricist_set = set()

    result = musicbrainzngs.search_works(query=f"work:{row['title']}", strict=False)


    for work in result['work-list']:
        found_composer_in_work = False

        if 'artist-relation-list' in work.keys():
            for artist in work['artist-relation-list']:
                for search_composer in composers:
                    if search_composer in artist['artist']['name'].lower():
                        print(f"\t\tfound {search_composer}, {artist['artist']['name']}, {artist['type']}")
                        if artist['type'] in ['composer', 'writer']:
                            composer_set.add(artist['artist']['name'])
                            found_composer_in_work = True
                        elif artist['type'] == 'lyricist':
                            lyricist_set.add(artist['artist']['name'])
                        else:
                            print(f"!!! warning: found {search_composer} but is a {artist['type']}.")

            # fallback: if the composer was found in this work, check if there is another composer or lyricist
            if found_composer_in_work:
                for artist in work['artist-relation-list']:
                    if artist['type'] in ['composer', 'writer']:
                        composer_set.add(artist['artist']['name'])
                        print(f"\t\tadditionally found {artist['artist']['name']}, {artist['type']}")
                    if artist['type'] == 'lyricist':
                        lyricist_set.add(artist['artist']['name'])
                        print(f"\t\tadditionally found {artist['artist']['name']}, {artist['type']}")
                break  # continue to the next tune


    df.at[index, 'composer_musicbrainz'] = list(composer_set)
    df.at[index, 'lyricist_musicbrainz'] = list(lyricist_set)

df.to_csv('tunes_musicbrainz.csv', sep='\t', encoding='utf8')


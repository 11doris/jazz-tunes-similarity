import musicbrainzngs
from wikidata.client import Client
import pandas as pd
import re
from dataset.utils import set_pandas_display_options


def _get_external_links(work_id):

    # WikiData Tags
    WIKIDATA_TAG_PUBLICATION = client.get('P577')
    WIKIDATA_TAG_TONALITY = client.get('P826')
    WIKIDATA_TAG_ALLMUSIC = client.get('P1994')

    _work = musicbrainzngs.get_work_by_id(work_id, includes=['url-rels'])
    if 'url-relation-list' not in _work['work'].keys():
        return None

    meta = {}

    for _url in _work['work']['url-relation-list']:
        #print(f"+ {_url['type']}: {_url['target']} +")
        if _url['type'] == 'wikidata':
            wikidata_id = _url['target'].split('/')[-1]
            wiki_entity = client.get(wikidata_id, load=True)
            meta['wikidata_id'] = wikidata_id
            meta['description'] = wiki_entity.description
            meta['publi_year'] = wiki_entity[WIKIDATA_TAG_PUBLICATION] if WIKIDATA_TAG_PUBLICATION in wiki_entity.keys() else None
            tonality = wiki_entity[WIKIDATA_TAG_TONALITY] if WIKIDATA_TAG_TONALITY in wiki_entity.keys() else None
            meta['tonality'] = tonality.label if tonality is not None else None
            meta['allmusic'] = wiki_entity[WIKIDATA_TAG_ALLMUSIC] if WIKIDATA_TAG_ALLMUSIC in wiki_entity.keys() else None
            meta['wiki_link'] = wiki_entity.data['sitelinks']['enwiki']['url'] if 'enwiki' in wiki_entity.data['sitelinks'] else None

            print(f"\t{meta['description']}") if meta['description'] is not None else None
            print(f"\tPublication Date: {meta['publi_year']}") if meta['publi_year'] is not None else None
            print(f"\tTonality: {meta['tonality']}") if meta['tonality'] is not None else None
            print(f"\tAllMusic: https://www.allmusic.com/composition/{meta['allmusic']}") if meta['allmusic'] is not None else None
            print(f"\t{meta['wiki_link']}") if meta['wiki_link'] is not None else None

    return meta



if __name__ == "__main__":

    # don't cut the display of data frames for debugging reasons
    set_pandas_display_options()

    # Initialize WikiData Client
    client = Client()

    # Tell musicbrainz what your app is, and how to contact you
    # (this step is required, as per the webservice access rules
    # at http://wiki.musicbrainz.org/XML_Web_Service/Rate_Limiting )
    musicbrainzngs.set_useragent("Jazz Maestro", "0.1", "http://example.com/music")

    # If you are connecting to a different server
    #musicbrainzngs.set_hostname("beta.musicbrainz.org")

    # read in the CSV file with the
    df = pd.read_csv('02_tunes_raw.csv', sep='\t', encoding='utf8')

    df['musicbrainz_id'] = ""
    df['musicbrainz_composer'] = ""
    df['musicbrainz_lyricist'] = ""
    df['musicbrainz_type'] = ""
    df['wikidata_id'] = ""
    df['wikidata_description'] = ""
    df['wikidata_year'] = ""
    df['wikidata_tonality'] = ""
    df['wikidata_allmusic'] = ""
    df['wiki_link'] = ""

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

        wiki_meta = {}
        result = musicbrainzngs.search_works(query=f"work:{row['title']}", strict=False)

        for work in result['work-list']:
            found_contributor = False

            if 'artist-relation-list' in work.keys():
                for artist in work['artist-relation-list']:
                    for search_composer in composers:
                        if search_composer in artist['artist']['name'].lower():
                            print(f"\t\tfound {search_composer}, {artist['artist']['name']}, {artist['type']}")
                            if artist['type'] in ['composer', 'writer']:
                                composer_set.add(artist['artist']['name'])
                                found_contributor = True
                            elif artist['type'] == 'lyricist':
                                lyricist_set.add(artist['artist']['name'])
                                found_contributor = True
                            else:
                                print(f"!!! warning: found {search_composer} but is a {artist['type']}.")

                # fallback: if the composer was found in this work, check if there is another composer or lyricist
                if found_contributor:
                    id = work['id']
                    type = work['type'] if 'type' in work.keys() else ""
                    wiki_meta = _get_external_links(id)
                    if wiki_meta is None:
                        print(f"\tNo links found for tune {row['title']}.")

                    for artist in work['artist-relation-list']:
                        if artist['type'] in ['composer', 'writer']:
                            composer_set.add(artist['artist']['name'])
                            print(f"\t\tadditionally found {artist['artist']['name']}, {artist['type']}")
                        if artist['type'] == 'lyricist':
                            lyricist_set.add(artist['artist']['name'])
                            print(f"\t\tadditionally found {artist['artist']['name']}, {artist['type']}")
                    break  # continue to the next tune

        df.at[index, 'musicbrainz_id'] = id
        df.at[index, 'musicbrainz_composer'] = sorted(list(composer_set))
        df.at[index, 'musicbrainz_lyricist'] = sorted(list(lyricist_set))
        df.at[index, 'musicbrainz_type'] = type
        if wiki_meta is not None:
            df.at[index, 'wikidata_id'] = wiki_meta['wikidata_id'] if 'wikidata_id' in wiki_meta.keys() else ""
            df.at[index, 'wikidata_description'] = wiki_meta['description'] if 'description' in wiki_meta.keys() else ""
            df.at[index, 'wikidata_year'] = wiki_meta['publi_year'] if 'publi_year' in wiki_meta.keys() else ""
            df.at[index, 'wikidata_tonality'] = wiki_meta['tonality'] if 'tonality' in wiki_meta.keys() else ""
            df.at[index, 'wikidata_allmusic'] = wiki_meta['allmusic'] if 'allmusic' in wiki_meta.keys() else ""
            df.at[index, 'wiki_link'] = wiki_meta['wiki_link'] if 'wiki_link' in wiki_meta.keys() else ""

    df['year'].astype('float')
    df.to_csv('02b_tunes_musicbrainz.csv', sep='\t', encoding='utf8', index=False)


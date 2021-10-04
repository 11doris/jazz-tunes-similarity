import musicbrainzngs
from wikidata.client import Client


## Choose the Tune to query
# tune = "A Blossom Fell"  # more information on webinterface available than on API! no composer on API.
tune = "all of me"
# tune = "all the things you are"
# tune = "how insensitive"
# tune = "it's you or no one"


# Initialize WikiData Client
client = Client()

# Tell musicbrainz what your app is, and how to contact you
# (this step is required, as per the webservice access rules
# at http://wiki.musicbrainz.org/XML_Web_Service/Rate_Limiting )
musicbrainzngs.set_useragent("Jazz Maestro", "0.1", "http://example.com/music")

# search MusicBrainz database
result = musicbrainzngs.search_works(query=tune, strict=True)
work_id = result['work-list'][0]['id']  # consider only first result for simplicity of this example

# WikiData Tags
WIKIDATA_TAG_PUBLICATION = client.get('P577')
WIKIDATA_TAG_TONALITY = client.get('P826')
WIKIDATA_TAG_ALLMUSIC = client.get('P1994')

work = musicbrainzngs.get_work_by_id(work_id, includes=['url-rels'])
if 'url-relation-list' not in work['work'].keys():
    print(f'No links found for tune {tune}. Exiting.')
    quit()

for _url in work['work']['url-relation-list']:
    print(f"+ {_url['type']}: {_url['target']} +")
    if _url['type'] == 'wikidata':
        wikidata_id = _url['target'].split('/')[-1]
        wiki_entity = client.get(wikidata_id, load=True)
        pub = wiki_entity[WIKIDATA_TAG_PUBLICATION] if WIKIDATA_TAG_PUBLICATION in wiki_entity.keys() else None
        tonality = wiki_entity[WIKIDATA_TAG_TONALITY] if WIKIDATA_TAG_TONALITY in wiki_entity.keys() else None
        allmusic = wiki_entity[WIKIDATA_TAG_ALLMUSIC] if WIKIDATA_TAG_ALLMUSIC in wiki_entity.keys() else None
        wiki_link = wiki_entity.data['sitelinks']['enwiki']['url'] if 'enwiki' in wiki_entity.data['sitelinks'] else None

        print(wiki_entity.description)
        print(f'Publication Date: {pub}') if pub is not None else None
        print(f'Tonality: {tonality.label}') if tonality is not None else None
        print(f'AllMusic: https://www.allmusic.com/composition/{allmusic}') if allmusic is not None else None
        print(wiki_link) if wiki_link is not None else None


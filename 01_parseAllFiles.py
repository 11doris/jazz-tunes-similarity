import os
import json
import re
import pandas as pd
import numpy as np
from chords.parseFile import parseFile


def metadata_cleaning(meta):

    df = pd.read_csv('./data_preparation/irealpro_manual_year.csv', sep='\t', encoding='utf8')

    for key, value in meta.items():
        row = df[df['file_name'].str.contains(key)]
        if len(row) > 0:
            if np.isnan(row['year'].values[0]):
                value['year'] = None
            else:
                value['year'] = int(row['year'].values[0])

        else:
            _composer_str = value['composer']
            # If the year is contained in the composer column, extract it to a new column
            m = re.search("\(?(18[0-9]{2}|19[0-9]{2}|20[0-9]{2})\)?", _composer_str)
            if m:
                value['year'] = int(m.group(1))
            else:
                value['year'] = None
            value["composer"] = re.sub(r"\(?(18[0-9]{2}|19[0-9]{2}|20[0-9]{2})\)?", "", _composer_str).strip()

        pattern = re.compile("\(Dixieland Tunes\)", re.IGNORECASE)
        value['title'] = pattern.sub("", value['title']).strip()

    return meta
        #
        # # Fix composer names
        # df['composer'] = df['composer'].str.replace("Van-Heusen", "Van Heusen", regex=False)
        # df['composer'] = df['composer'].str.replace("Armstroong", "Louis Armstrong", regex=False)
        # df['composer'] = df['composer'].str.replace("Antonio-Carlos", "Antonio Carlos", regex=False)



if __name__ == "__main__":
    ##
    # read config file
    config = json.load(open('config.json'))

    # read directory names containing the MusicXML input files
    xmldirectories = config['xmldirectory'][config['config']['input']]

    ##
    #
    files = []
    for directory in xmldirectories:
        for file in os.listdir(directory):
            files.append(os.path.join(directory, file))

    print(f'Found {len(files)} files to parse... ')

    # parse the MusicXML files and generate a json object with the chords information
    out = {}
    composers = {}
    keys = {}
    meta_info = {}

    for file in files:
        print(file)
        out[file], key, mode, composer, sections, num_bars, max_num_chords_per_bar = parseFile(file)
        composers[file] = composer
        keys[file] = {'key': key,
                      'mode': mode}
        meta_info[file] = {'title': os.path.splitext(os.path.basename(file))[0],
                          'default_key': {'key': key,
                                          'mode': mode
                                          },
                          'composer': composer,
                          'sections': sections,
                          'num_bars': num_bars,
                          'max_num_chords_per_bar': max_num_chords_per_bar,
                          }

    meta_info = metadata_cleaning(meta_info)

    f = open("dataset/chords.json", "w")
    f.write(json.dumps(out, indent=2))
    f.close()

    f = open("dataset/meta_info.json", "w")
    f.write(json.dumps(meta_info, indent=2))
    f.close()

    f = open("dataset/keys.json", "w")
    f.write(json.dumps(keys, indent=2))
    f.close()

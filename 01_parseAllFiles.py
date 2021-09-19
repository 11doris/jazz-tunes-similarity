import os
import json
import re
import pandas as pd
import numpy as np
from chords.parseFile import parseFile


def __add_year_from_musicxml_and_clean(meta):
    for key, value in meta.items():
        _composer_str = value['composer']

        # If the year is contained in the composer column, extract it to a new column
        m = re.search("\(?(18[0-9]{2}|19[0-9]{2}|20[0-9]{2})\)?", _composer_str)
        if m:
            value['year'] = int(m.group(1))
            value["composer"] = re.sub(r"\(?(18[0-9]{2}|19[0-9]{2}|20[0-9]{2})\)?", "", _composer_str).strip()
        else:
            value['year'] = None

        # clean title
        pattern = re.compile("\(Dixieland Tunes\)", re.IGNORECASE)
        value['title'] = pattern.sub("", value['title']).strip()

        # clean composer names
        value['composer'] = value['composer'].replace("Van-Heusen", "Van Heusen")
        value['composer'] = value['composer'].replace("Armstroong", "Louis Armstrong")
        value['composer'] = value['composer'].replace("Antonio-Carlos", "Antonio Carlos")
        value['composer'] = value['composer'].replace("De-Rose", "DeRose")
        value['composer'] = value['composer'].replace("Matt Maineck", "Matty Malneck")

    return meta


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
        out[file], info = parseFile(file)
        meta_info[file] = info
        meta_info[file]['title'] = os.path.splitext(os.path.basename(file))[0]
        meta_info[file]['file_path'] = file

    # extract the year from the Composer if available, do some cleaning
    meta_info = __add_year_from_musicxml_and_clean(meta_info)

    # dump to files
    f = open("dataset/chords.json", "w")
    f.write(json.dumps(out, indent=2))
    f.close()

    f = open("dataset/meta_info.json", "w")
    f.write(json.dumps(meta_info, indent=2))
    f.close()


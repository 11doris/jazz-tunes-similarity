import os
import json
from chords.parseFile import parseFile

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

for i, file in enumerate(files):
    print(file)
    out[file], key, mode, composer, sections, num_bars, max_num_chords_per_bar = parseFile(file)
    composers[file] = composer
    keys[file] = {'key': key,
                  'mode': mode}
    meta_info[i] = {'title': os.path.splitext(os.path.basename(file))[0],
                      'default_key': {'key': key,
                                      'mode': mode
                                      },
                      'composer': composer,
                      'sections': sections,
                      'num_bars': num_bars,
                      'max_num_chords_per_bar': max_num_chords_per_bar,
                      'file_path': file,
                      }

f = open("dataset/chords.json", "w")
f.write(json.dumps(out, indent=2))
f.close()

f = open("dataset/meta_info.json", "w")
f.write(json.dumps(meta_info, indent=2))
f.close()

f = open("dataset/keys.json", "w")
f.write(json.dumps(keys, indent=2))
f.close()

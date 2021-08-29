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
durations = {}
composers = {}
keys = {}
meta_info = {}

for i, file in enumerate(files):
    print(file)
    out[file], durations[file], info = parseFile(file)
    meta_info[file] = info
    meta_info[file]['title'] = os.path.splitext(os.path.basename(file))[0]
    meta_info[file]['file_path'] = file


f = open("dataset/chords.json", "w")
f.write(json.dumps(out, indent=2))
f.close()

f = open("dataset/durations.json", "w")
f.write(json.dumps(durations, indent=2))
f.close()

f = open("dataset/meta_info.json", "w")
f.write(json.dumps(meta_info, indent=2))
f.close()

f
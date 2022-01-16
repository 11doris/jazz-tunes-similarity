from chords.parseFile import parseFile
from chords.chord import Chord
from dataset.readData import ReadData
import json


def test_chords():
    files = ['./fixtures/All Chords Part1.xml',
             './fixtures/All Chords Part2.xml']

    out = {}
    meta_info = {}

    for file in files:
        out[file], info = parseFile(file)
        meta_info[file] = info

    assert info['num_bars'] == 28
    assert info['max_num_chords_per_bar'] == 1

    tunes_path = "test_parse_file_chords.json"
    f = open(tunes_path, "w")
    f.write(json.dumps(out, indent=2))
    f.close()

    meta_path = "test_parse_file_meta.json"
    f = open(meta_path, "w")
    f.write(json.dumps(meta_info, indent=2))
    f.close()


    # read in the data
    data_obj = ReadData()
    data_obj.set_json_paths(tunes_path=tunes_path, meta_path=meta_path)
    data, names, beats = data_obj.rootAndDegrees()

    sequences = []
    for i in range(len(data)):
        tune = data[i]
        seq = []
        for chord in tune:
            formatted_chord = Chord(chord).toSymbol(key=3,
                                                    includeRoot=True,
                                                    includeBass=False)
            seq += [formatted_chord]
        sequences += [seq]

    correct_chords = [
        [
            'C', 'CM7', 'Cm7', 'C7',
            'C7sus4', 'CM7', 'Cm', 'C7alt',
            'Csus4', 'C6', 'Cm6', 'Cdim7',
            'Cm7b5', 'CM9', 'Cm9', 'C9',
            'C9sus4', 'CM13', 'Cm11', 'C11',
            'C13', 'C13sus4', 'C6(+9)', 'Cm6(+9)',
            'CmM7','CmM9', 'CM7(+#11)', 'CM9(+#11)',
            'Cm(+b6)'
        ],
        [
            'Cmaug', 'CdimM7', 'CaugM7', 'C(+9)',
            'Cm(+9)', 'Cm7b5', 'Cm7b5(+9)', 'C(+9)',
            'C5', 'Caug', 'Cdim', 'Cm7b5',
            'C7(+b9)', 'C7(+#9)', 'C7(+b5)', 'Caug7',
            'C7(+b13)', 'C7(+#11)', 'C9(+#11)', 'C13(+#11)',
            'C7(+b9)(+b13)', 'Caug7(+b9)', 'C7(+b5)(+b9)', 'C7(+b9)(+#9)',
            'Caug7(+#9)', 'C7(+b5)(+#9)', 'C7(+#9)(+#11)', 'C7(+b9)(+#11)'
        ]
    ]

    print()
    errors = 0
    for i in range(len(sequences)):
        for num, chord in enumerate(sequences[i]):
            if chord != correct_chords[i][num]:
                errors += 1
                print(num + 1, chord, f'!! Wrong - should be {correct_chords[i][num]}')
            else:
                print(num + 1, chord)

    assert errors == 0


def test_chords_chordsSimplified():
    files = ['./fixtures/All Chords Part1.xml',
             './fixtures/All Chords Part2.xml']

    out = {}
    meta_info = {}

    for file in files:
        out[file], info = parseFile(file)
        meta_info[file] = info

    assert info['num_bars'] == 28
    assert info['max_num_chords_per_bar'] == 1

    tunes_path = "test_parse_file_chords.json"
    f = open(tunes_path, "w")
    f.write(json.dumps(out, indent=2))
    f.close()

    meta_path = "test_parse_file_meta.json"
    f = open(meta_path, "w")
    f.write(json.dumps(meta_info, indent=2))
    f.close()


    # read in the data
    data_obj = ReadData()
    data_obj.set_json_paths(tunes_path=tunes_path, meta_path=meta_path)

    # generate the chord sequence
    data, names, beats = data_obj.chordsSimplified()

    sequences = []
    for i in range(len(data)):
        tune = data[i]
        seq = []
        for chord in tune:
            formatted_chord = Chord(chord).toSymbol(key=3,
                                                    includeRoot=True,
                                                    includeBass=False)
            seq += [formatted_chord]
        sequences += [seq]

    correct_chords = [
        [
            'C', 'CM7', 'Cm7', 'C7',
            'C7sus4', 'CM7', 'Cm', 'C7(+b5)',
            'Csus4', 'C6', 'Cm6', 'Cdim7',
            'Cm7b5', 'CM7', 'Cm7', 'C7',
            'C7sus4', 'CM7', 'Cm7', 'C7sus4',
            'C7', 'C7sus4', 'C6', 'Cm6',
            'CmM7', 'CmM7', 'CM7', 'CM7',
            'Cm(+b6)'
        ],
        [
            'Cmaug', 'CdimM7', 'CaugM7', 'C',
            'Cm', 'Cm7b5', 'Cm7b5', 'C',
            'C', 'Caug', 'Cdim', 'Cm7b5',
            'C7', 'C7', 'C7(+b5)', 'Caug7',
            'C7', 'C7', 'C7', 'C7',
            'C7', 'Caug7', 'C7(+b5)', 'C7',
            'Caug7', 'C7(+b5)', 'C7', 'C7'
        ]
    ]

    print()
    errors = 0
    for i in range(len(sequences)):
        for num, chord in enumerate(sequences[i]):
            if chord != correct_chords[i][num]:
                errors += 1
                print(num + 1, chord, f'!! Wrong - should be {correct_chords[i][num]}')
            else:
                print(num + 1, chord)

    assert errors == 0



def test_chords_chordsBasic():
    files = ['./fixtures/All Chords Part1.xml',
             './fixtures/All Chords Part2.xml']

    out = {}
    meta_info = {}

    for file in files:
        out[file], info = parseFile(file)
        meta_info[file] = info

    assert info['num_bars'] == 28
    assert info['max_num_chords_per_bar'] == 1

    tunes_path = "test_parse_file_chords.json"
    f = open(tunes_path, "w")
    f.write(json.dumps(out, indent=2))
    f.close()

    meta_path = "test_parse_file_meta.json"
    f = open(meta_path, "w")
    f.write(json.dumps(meta_info, indent=2))
    f.close()


    # read in the data
    data_obj = ReadData()
    data_obj.set_json_paths(tunes_path=tunes_path, meta_path=meta_path)

    # generate the chord sequence
    data, names, beats = data_obj.chordsBasic()

    # print()
    # for i in data[1]:
    #     print(i)

    sequences = []
    for i in range(len(data)):
        tune = data[i]
        seq = []
        for chord in tune:
            formatted_chord = Chord(chord).toSymbol(key=3,
                                                    includeRoot=True,
                                                    includeBass=False)
            seq += [formatted_chord]
        sequences += [seq]

    correct_chords = [
        [
            'C', 'C', 'Cm', 'C7',
            'C7sus4', 'C', 'Cm', 'C7(+b5)',
            'Csus4', 'C', 'Cm', 'Cdim',
            'Cm7b5', 'C', 'Cm', 'C7',
            'C7sus4', 'C', 'Cm', 'C7',
            'C7', 'C7sus4', 'C', 'Cm',
            'Cm', 'Cm', 'C', 'C',
            'Cm(+b6)'
        ],
        [
            'Cmaug', 'Cdim', 'Caug', 'C',
            'Cm', 'Cm7b5', 'Cm7b5', 'C',
            'C', 'Caug', 'Cdim', 'Cm7b5',
            'C7', 'C7', 'C7(+b5)', 'Caug7',
            'C7', 'C7', 'C7', 'C7',
            'C7', 'Caug7', 'C7(+b5)', 'C7',
            'Caug7', 'C7(+b5)', 'C7', 'C7'
        ]
    ]

    print()
    errors = 0
    for i in range(len(sequences)):
        for num, chord in enumerate(sequences[i]):
            if chord != correct_chords[i][num]:
                errors += 1
                print(num + 1, chord, f'!! Wrong - should be {correct_chords[i][num]} but is {chord}')
            else:
                print(num + 1, chord)

    assert errors == 0


def test_chords_for_leadsheet():
    files = ['./fixtures/All Chords Part1.xml',
             './fixtures/All Chords Part2.xml']

    out = {}
    meta_info = {}

    for file in files:
        out[file], info = parseFile(file)
        meta_info[file] = info

    assert info['num_bars'] == 28
    assert info['max_num_chords_per_bar'] == 1

    tunes_path = "test_parse_file_chords.json"
    f = open(tunes_path, "w")
    f.write(json.dumps(out, indent=2))
    f.close()

    meta_path = "test_parse_file_meta.json"
    f = open(meta_path, "w")
    f.write(json.dumps(meta_info, indent=2))
    f.close()


    # read in the data
    data_obj = ReadData()
    data_obj.set_json_paths(tunes_path=tunes_path, meta_path=meta_path)
    data, names, beats = data_obj.rootAndDegrees()

    sequences = []
    for i in range(len(data)):
        tune = data[i]
        seq = []
        for chord in tune:
            formatted_chord = Chord(chord).toHtmlLeadSheet(key=11,
                                                    includeRoot=True,
                                                    includeBass=False)
            seq += [formatted_chord]
        sequences += [seq]

    print()
    errors = 0


    assert errors == 0
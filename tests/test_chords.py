from chords.parseFile import parseFile
from chords.chord import Chord
from dataset.readData import ReadData
import json


def test_chords():
    files = ['./fixtures/All Chords Part1.xml',
             './fixtures/All Chords Part2.xml']

    out = {}
    for file in files:
        out[file], key, mode, composer, sections, num_bars, max_num_chords_per_bar = parseFile(file)

    assert num_bars == 28
    assert max_num_chords_per_bar == 1

    file_path = "test_parse_file_chords.json"
    f = open(file_path, "w")
    f.write(json.dumps(out, indent=2))
    f.close()

    # read in the data
    data_obj = ReadData()
    data_obj.read_tunes(file_path=file_path)
    data, names = data_obj.rootAndDegrees()

    sequences = []
    for i in range(len(data)):
        tune = data[i]
        seq = []
        for chord in tune:
            formatted_chord = Chord(chord).toSymbol(key=key,
                                                    includeRoot=True,
                                                    includeBass=False)
            seq += [formatted_chord]
        sequences += [seq]


    correct_chord_representation = [
        [
            'C', 'CM7', 'Cm7', 'C7',
            'C7sus', 'CM7', 'Cm', 'C7alt',
            'Csus4', 'C6', 'Cm6', 'Cdim7',
            'Cm7b5', 'CM9', 'Cm9', 'C9',
            'C9sus4', 'CM13', 'Cm11', 'C13',
            'C13sus4', 'C6(+9)', 'Cm6(+9)', 'CmM7',
            'CmM9', 'CM7(+#11)', 'CM9(+#11)', 'Cm(-b6)'
        ],
        [
            'Cmaug', 'CdimM7', 'CaugM7', 'C(+9)',
            'Cm(+9)', 'Cm7b5', 'Cø9', 'C2',
            'C5', 'Caug', 'Cdim', 'Cø',
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
            if chord != correct_chord_representation[i][num]:
                errors += 1
                print(num + 1, chord, '!! Wrong')
            else:
                print(num + 1, chord)

    assert errors == 0

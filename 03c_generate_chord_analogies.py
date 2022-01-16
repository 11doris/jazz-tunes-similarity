import numpy as np
import pandas as pd
from chords.symbol.parts.noteSymbol import Note

#
# Credits: the following code is based on https://github.com/SaxMan96/Harmony-Analyzer/blob/master/testing_embeddings.py
#

def generate_validation_file(file_name):
    test_list = []
    test_dict = {}

    note_object = Note("")
    KEYS = note_object.unique

    print('minor to dominant progressions')
    chord_1 = 'm'
    chord_2 = '7'
    interval = 0
    for note in range(len(KEYS)):
        for diff in range(1, len(KEYS)):
            row = KEYS[note] + chord_1 + " " + KEYS[(note + interval) % 12] + chord_2 + " " + KEYS[
                (diff + note) % 12] + chord_1 + " " + KEYS[(diff + note + interval) % 12] + chord_2
            test_list.append(row)
    test_dict[": minor-to-dominant"] = test_list
    test_list = []

    print('major to minor progressions')
    chord_1 = ''
    chord_2 = 'm'
    interval = 0
    for note in range(len(KEYS)):
        for diff in range(1, len(KEYS)):
            row = KEYS[note] + chord_1 + " " + KEYS[(note + interval) % 12] + chord_2 + " " + KEYS[
                (diff + note) % 12] + chord_1 + " " + KEYS[(diff + note + interval) % 12] + chord_2
            test_list.append(row)
    test_dict[": major-to-minor"] = test_list
    test_list = []

    print('dominant to minor progressions')
    chord_1 = '7'
    chord_2 = 'm'
    interval = 0
    for note in range(len(KEYS)):
        for diff in range(1, len(KEYS)):
            row = KEYS[note] + chord_1 + " " + KEYS[(note + interval) % 12] + chord_2 + " " + KEYS[
                (diff + note) % 12] + chord_1 + " " + KEYS[(diff + note + interval) % 12] + chord_2
            test_list.append(row)
    test_dict[": dominant-to-minor"] = test_list
    test_list = []

    print('dominant-to-minor half-step down')
    chord_1 = '7'
    chord_2 = 'm'
    interval = -1
    for note in range(len(KEYS)):
        for diff in range(1, len(KEYS)):
            row = KEYS[note] + chord_1 + " " + KEYS[(note + interval) % 12] + chord_2 + " " + KEYS[
                (diff + note) % 12] + chord_1 + " " + KEYS[(diff + note + interval) % 12] + chord_2
            test_list.append(row)
    test_dict[": dominant-to-minor-half-step-down"] = test_list
    test_list = []

    print('minor-to-dominant half-step down')
    chord_1 = 'm'
    chord_2 = '7'
    interval = -1
    for note in range(len(KEYS)):
        for diff in range(1, len(KEYS)):
            row = KEYS[note] + chord_1 + " " + KEYS[(note + interval) % 12] + chord_2 + " " + KEYS[
                (diff + note) % 12] + chord_1 + " " + KEYS[(diff + note + interval) % 12] + chord_2
            test_list.append(row)
    test_dict[": minor-to-dominant-half-step-down"] = test_list
    test_list = []

    print('V-I progressions')
    chord_1 = '7'
    chord_2 = ''
    interval = 5
    for note in range(len(KEYS)):
        for diff in range(1, len(KEYS)):
            row = KEYS[note] + chord_1 + " " + KEYS[(note + interval) % 12] + chord_2 + " " + KEYS[
                (diff + note) % 12] + chord_1 + " " + KEYS[(diff + note + interval) % 12] + chord_2
            test_list.append(row)
    test_dict[": V-I"] = test_list
    test_list = []

    print('II-V progressions')
    chord_1 = 'm'
    chord_2 = '7'
    interval = 5
    for note in range(len(KEYS)):
        for diff in range(1, len(KEYS)):
            row = KEYS[note] + chord_1 + " " + KEYS[(note + interval) % 12] + chord_2 + " " + KEYS[
                (diff + note) % 12] + chord_1 + " " + KEYS[(diff + note + interval) % 12] + chord_2
            test_list.append(row)
    test_dict[": ii-V"] = test_list
    test_list = []

    print('generate V/V-V_progression')
    chord = '7'
    interval = 5
    for note in range(len(KEYS)):
        for diff in range(1, len(KEYS)):
            row = KEYS[note] + chord + " " + KEYS[(note + interval) % 12] + chord + " " + KEYS[
                (diff + note) % 12] + chord + " " + KEYS[(diff + note + interval) % 12] + chord
            test_list.append(row)
    test_dict[": V/V-V"] = test_list

    test_list = []
    for k, v in zip(test_dict.keys(), test_dict.values()):
        test_list.append(k)
        test_list = test_list + v

    print(f"Generated {len(test_list)} chord analogies.")
    print("Saving test file: " + file_name)
    pd.DataFrame(test_list).to_csv('tests/fixtures/' + file_name, header=None, index=False)


if __name__ == "__main__":
    generate_validation_file(file_name="test_chord_analogies.txt")

from chords.ChordSequence import ChordSequence
from dataset.utils import set_pandas_display_options

if __name__ == "__main__":
    set_pandas_display_options()

    cs = ChordSequence(chord_style='ascii')

    # get data including section info
    cs.split_tunes_in_sections(chords='chordsBasic')
    cs.split_tunes_in_sections(chords='chordsSimplified')
    cs.split_tunes_in_sections(chords='chordsFull')

    print("Done.")

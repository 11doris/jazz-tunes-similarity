from chords.ChordSequence import ChordSequence
from dataset.utils import set_pandas_display_options
import pandas as pd
from data_preparation.utils import output_preprocessing_directory


if __name__ == "__main__":
    set_pandas_display_options()

    cs = ChordSequence(chord_style='ascii')

    # get data including section info
    cs.split_tunes_in_sections(chords='rootAndDegreesPlus')
    cs.split_tunes_in_sections(chords='simplified')

    print("Done.")

from chords.ChordSequence import ChordSequence
from dataset.utils import set_pandas_display_options
import pandas as pd


if __name__ == "__main__":
    set_pandas_display_options()

    cs = ChordSequence(chord_style='ascii')

    # get data including section info
    cs.split_tunes_in_sections(chords='rootAndDegreesPlus')
    cs.split_tunes_in_sections(chords='simplified')

    # # get data for tunes
    # df = cs.get_tunes_data()
    # df.to_csv('03b_input_model_tunes.csv', sep='\t', encoding='utf-8', index=True, index_label="id")

    print("Done.")

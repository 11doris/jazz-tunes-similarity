from chords.ChordSequence import ChordSequence
from dataset.utils import set_pandas_display_options
import pandas as pd


if __name__ == "__main__":
    set_pandas_display_options()

    cs = ChordSequence()

    seq = cs.create_embedding_input()

    print("Write generated chord sequence to file...")
    with open('03b_input_word_embedding.txt', 'w') as f:
        for tune in seq:
            line = ", ".join([", ".join(x) for x in tune])
            f.write(f"{line}\n")

    print("Done.")


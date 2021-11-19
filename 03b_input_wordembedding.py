from chords.ChordSequence import ChordSequence
from dataset.utils import set_pandas_display_options
import pandas as pd


if __name__ == "__main__":
    set_pandas_display_options()

    cs = ChordSequence()

    # get data including section info
    df = cs.split_tunes_in_sections()
    df.to_csv('03b_input_wordembedding_sections.csv', sep='\t', encoding='utf-8', index=True, index_label="id")

    # embedding input
    seq = cs.create_embedding_input()

    print("Write generated chord sequence to file...")
    with open('03b_input_word_embedding.txt', 'w') as f:
        for tune in seq:
            line = " ".join(tune)
            f.write(f"{line}\n")

    # get data for Topics
    seq = cs.create_topics_input()
    print("Write generated chord sequence for Topics to file...")
    with open('03c_input_topics.txt', 'w') as f:
        for tune in seq:
            line = " ".join(tune)
            f.write(f"{line}\n")

    print("Done.")

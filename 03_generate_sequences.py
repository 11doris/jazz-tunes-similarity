from chords.ChordSequence import ChordSequence
import pandas as pd
from dataset.utils import set_pandas_display_options


if __name__ == "__main__":
    set_pandas_display_options()

    cs = ChordSequence()
    df = cs.generate_sequences()

    print(df.head(50))

    #meta = pd.read_csv('02c_tune_sql_import.csv', sep='\t')

    file_name = 'dataset/test3/500 Miles High.xml'
    file_name = 'dataset/test3/Take Five.xml'

    dd = df.query(f'file_name == "{file_name}"')

    ## Write Lead Sheet as a Markdown Table

    # define number of bars per line
    if len(dd.query(f'SectionLabel == "A"')) % 5 == 0:
        num_bars_per_line = 5
    else:
        num_bars_per_line = 4

    # generate the table header (mandatory for markdown tables)
    leadsheet = "| ".join([""] * (num_bars_per_line + 1)) + "|\n"
    leadsheet += "| --- ".join([""] * (num_bars_per_line + 1)) + "|\n"
    line = ""

    # generate table content
    for index, row in dd.iterrows():
        # last measure per line
        if row['MeasureNum'] % num_bars_per_line == 0:
            chords = ", ".join(row['Chords'])
            line += f"| {chords} |\n"
            leadsheet += line
            line = ""
        else:
            chords = ", ".join(row['Chords'])
            line += f"| {chords}"

    print(leadsheet)


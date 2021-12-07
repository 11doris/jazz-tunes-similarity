import pandas as pd
from dataset.utils import set_pandas_display_options


set_pandas_display_options()

df = pd.read_csv('03_chords_sql_import.csv', sep='\t')
df.head()

dd = df.query(f'id == 58')

last_measure = 1
last_beat = 1
bar = ""
lines = ""
html_str = ""

for index, row in dd.iterrows():
    print(row['MeasureNum'], row['Beat'])

    if row['MeasureNum'] == last_measure:
        while row["Beat"] - 1 > last_beat:
            last_beat += 1
            bar += f'html.Div("", className="beat b{last_beat}"),'

        bar += f'html.Div("{row["ChordRelative"]}", className="beat b{row["Beat"]}"),'
        print("Bar: ", bar)

    elif row['MeasureNum'] != last_measure:
        # finish the previous measure
        measure_num = last_measure % 4
        measure_num = 4 if measure_num == 0 else measure_num
        m = f'html.Div(html.Div([{bar}],className="beat-wrapper",),className="measure m{measure_num}",),'
        print(m)
        lines += m
        last_beat = 1

        # get the chord of the current measure and bar
        bar = ""
        bar += f'html.Div("{row["ChordRelative"]}", className="beat b{row["Beat"]}"),'
        last_measure = row["MeasureNum"]

# finish the last bar
if row['MeasureNum'] == last_measure:
    measure_num = last_measure % 4
    measure_num = 4 if measure_num == 0 else measure_num
    m = f'html.Div(html.Div([{bar}],className="beat-wrapper",),className="measure m{measure_num}",),'
    print(m)
    lines += m

html_str = f'html.Div([{lines}],className="wrapper",),'

print("Result:")
print(html_str)

#lines Someday youll be sorry with 1,3,4 is wrong!


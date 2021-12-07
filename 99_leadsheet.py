import pandas as pd
from dataset.utils import set_pandas_display_options


set_pandas_display_options()

df = pd.read_csv('03_chords_sql_import.csv', sep='\t')
df.head()

dd = df.query(f'id == 58')

last_measure = 1
bar = ""
lines = ""
html_str = ""

for index, row in dd.iterrows():
    print(row['MeasureNum'], row['Beat'])

    if row['MeasureNum'] == last_measure:
        bb = f'html.Div("{row["ChordRelative"]}", className="beat b{row["Beat"]}"),'
        bar += bb
        print("Bar: ", bar)

    elif row['MeasureNum'] != last_measure:
        # finish the previous measure
        measure_num = last_measure % 4
        measure_num = 4 if measure_num == 0 else measure_num
        m = f'html.Div(html.Div([{bar}],className="beat-wrapper",),className="measure m{measure_num}",),'
        print(m)
        lines += m

        # get the chord of the current measure and bar
        bar = ""
        bb = f'html.Div("{row["ChordRelative"]}", className="beat b{row["Beat"]}"),'
        bar += bb
        last_measure = row["MeasureNum"]

# finish the last bar
if row['MeasureNum'] == last_measure:
    measure_num = last_measure % 4
    measure_num = 4 if measure_num == 0 else measure_num
    m = f'html.Div(html.Div([{bar}],className="beat-wrapper",),className="measure m{measure_num}",),'
    print(m)
    lines += m



html_str = f'html.Div([{lines}],className="wrapper",),'

print(html_str)
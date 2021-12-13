import pandas as pd
from dataset.utils import set_pandas_display_options


def get_html_chord_format(row):
    return f'''
    html.Div([
      html.Div("{row["relative_Root1"]}", className="root"),
      html.Div([
        html.Div("", className="{row["relative_Root2"]}"),
        html.Div("{row["chord_down"]}", className="down"),
        ],
      className="add",
      ),
      html.Div([
        html.Div("{row["chord_alt_up"]}", className="alt-up"),
        html.Div("{row["chord_alt_down"]}", className="alt-down"),
        ],
        className="alteration",
      ),
      ],
      className="chord",
    ),
    '''

set_pandas_display_options()

df = pd.read_csv('03_chords_sql_import.csv', sep='\t')
df.head()

#dd = df.query(f'id == 1060')  # Someday you'll be sorry
dd = df.query(f'id == 685')   # Laurie

last_measure = 1
last_beat = 0
bar = ""
lines = ""
html_str = ""

# Add first section label
section_label = dd['SectionLabel'].iloc[0] if dd['StartOfSection'].iloc[0] else ""
s = f'html.Div("{section_label}", className="section"),'
lines += s

for index, row in dd.iterrows():
#    print(row['SectionLabel'], row['StartOfSection'])
#    print(row['MeasureNum'], row['Beat'])


    if row['MeasureNum'] == last_measure:
        while row["Beat"] - 1 > last_beat:
            last_beat += 1
            bar += f'html.Div("", className="beat b{last_beat}"),'

        bar += f'html.Div({get_html_chord_format(row)} className="beat b{row["Beat"]}"),'
        last_beat += 1
        #print("Bar: ", bar)

    elif row['MeasureNum'] != last_measure:
        # finish the previous measure
        measure_num = last_measure % 4
        measure_num = 4 if measure_num == 0 else measure_num
        m = f'html.Div(html.Div([{bar}],className="beat-wrapper",),className="measure m{measure_num}",),'
#        print(m)
        lines += m
        last_beat = 1

        # if the previous measure was measure 4, add the section label next
        if measure_num == 4:
            section_label = row['SectionLabel'] if row['StartOfSection'] else ""
            s = f'html.Div("{section_label}", className="section"),'
            lines += s

        # get the chord of the current measure and bar
        bar = ""
        bar += f'html.Div({get_html_chord_format(row)} className="beat b{row["Beat"]}"),'
        last_measure = row["MeasureNum"]

# finish the last bar
if row['MeasureNum'] == last_measure:
    measure_num = last_measure % 4
    measure_num = 4 if measure_num == 0 else measure_num
    m = f'html.Div(html.Div([{bar}],className="beat-wrapper",),className="measure m{measure_num}",),'
#    print(m)
    lines += m

html_str = f'html.Div([{lines}],className="wrapper",),'

print("Result:")
print(html_str)


import pandas as pd
from dataset.utils import set_pandas_display_options


def get_html_chord_format(row, relative=True):
    if relative:
        root1 = "relative_Root1"
        root2 = "relative_Root2"
    else:
        root1 = "default_Root1"
        root2 = "default_Root2"

    return f'''
    html.Div([
      html.Div("{row[root1]}", className="root"),
      html.Div([
        html.Div("", className="{row[root2]}"),
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


def generate_html_leadsheet(df: pd.DataFrame, relative=True):
    last_measure = 1
    last_beat = 0
    bar = ""
    lines = ""
    html_str = ""

    # Add first section label
    section_label = df['SectionLabel'].iloc[0] if df['StartOfSection'].iloc[0] else ""
    s = f'html.Div("{section_label}", className="section"),'
    lines += s

    for index, row in df.iterrows():
        #    print(row['SectionLabel'], row['StartOfSection'])
        #    print(row['MeasureNum'], row['Beat'])

        if row['MeasureNum'] == last_measure:
            while row["Beat"] - 1 > last_beat:
                last_beat += 1
                bar += f'html.Div("", className="beat b{last_beat}"),'

            bar += f'html.Div({get_html_chord_format(row, relative)} className="beat b{row["Beat"]}"),'
            last_beat += 1
            # print("Bar: ", bar)

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
            bar += f'html.Div({get_html_chord_format(row, relative)} className="beat b{row["Beat"]}"),'
            last_measure = row["MeasureNum"]

    # finish the last bar
    if row['MeasureNum'] == last_measure:
        measure_num = last_measure % 4
        measure_num = 4 if measure_num == 0 else measure_num
        m = f'html.Div(html.Div([{bar}],className="beat-wrapper",),className="measure m{measure_num}",),'
        #    print(m)
        lines += m

    html_str = f'html.Div([{lines}],className="wrapper",),'

    return html_str


##
#
if __name__ == "__main__":

    set_pandas_display_options()

    all = pd.read_csv('03_chords_sql_import.csv', sep='\t')
    all.head()

    #dd = df.query(f'id == 1060')  # Someday you'll be sorry
    df = all.query(f'id == 685')   # Laurie

    html_str = generate_html_leadsheet(df, relative=True)

    print("Result:")
    print(html_str)


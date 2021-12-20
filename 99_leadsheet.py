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
    last_measure_absolut = 1
    last_measure_on_line = 1
    last_beat = 0
    bar = ""
    lines = ""

    debug = False

    # Add first section label
    section_label = df['SectionLabel'].iloc[0] if df['StartOfSection'].iloc[0] else ""
    s = f'html.Div("{section_label}", className="section"),'
    lines += s

    for index, row in df.iterrows():
        if debug:
            print(row['SectionLabel'], row['StartOfSection'])
            print(row['MeasureNum'], row['Beat'])

        # we're still handling chords in the same measure
        if row['MeasureNum'] == last_measure_absolut:
            while row["Beat"] - 1 > last_beat:
                last_beat += 1
                bar += f'html.Div("", className="beat b{last_beat}"),'

            bar += f'html.Div({get_html_chord_format(row, relative)} className="beat b{row["Beat"]}"),'
            last_beat += 1

        # now we're in a new measure
        elif row['MeasureNum'] != last_measure_absolut:
            # finish the previous measure
            measure_num = last_measure_on_line % 4
            measure_num = 4 if measure_num == 0 else measure_num

            # increase the counter which counts the bar number on the current line
            last_measure_on_line += 1

            m = f'html.Div(html.Div([{bar}],className="beat-wrapper",),className="measure m{measure_num}",),'
            lines += m
            last_beat = 1

            # Add the section label next if we're at the last measure or a new section starts
            if (measure_num == 4) or (row['StartOfSection']):
                s = ""
                # if a new section starts and we're not at the end of the line, fill up the line with empty bars
                if (measure_num < 4) and (row['StartOfSection']):
                    # if a new section starts before measure 4, start a new line
                    s += f'html.Div("",className="left-double-bar"),'
                    for i in range(measure_num+1, 4):
                        s += f'html.Div("",className="section"),'

                section_label = row['SectionLabel'] if row['StartOfSection'] else ""
                s += f'html.Div("{section_label}", className="section"),'

                lines += s
                last_measure_on_line = 1

            # get the chord of the current measure and bar
            bar = ""
            bar += f'html.Div({get_html_chord_format(row, relative)} className="beat b{row["Beat"]}"),'
            last_measure_absolut = row["MeasureNum"]

            if debug:
                print(f'last_abs: {last_measure_absolut}, last_rel: {last_measure_on_line}')

    # finish the last bar
    if row['MeasureNum'] == last_measure_absolut:
        measure_num = last_measure_absolut % 4
        measure_num = 4 if measure_num == 0 else measure_num
        m = f'html.Div(html.Div([{bar}],className="beat-wrapper",),className="measure m{measure_num}",),'
        #    print(m)
        lines += m

    return f'html.Div([{lines}],className="wrapper",),'



##
#
if __name__ == "__main__":

    set_pandas_display_options()

    all = pd.read_csv('03_chords_sql_import.csv', sep='\t')
    all.head()

    #df = all.query(f'id == 1060')  # Someday you'll be sorry
    #df = all.query(f'id == 685')   # Laurie
    df = all.query(f'id == 69')    # Alone Together

    html_str = generate_html_leadsheet(df, relative=True)

    print("Result:")
    #print(html_str)


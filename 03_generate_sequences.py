from database.api import using_alchemy
from sqlalchemy import text
from chords.ChordSequence import ChordSequence
from dataset.utils import set_pandas_display_options


def insert_to_sql(df):
    engine = using_alchemy()

    table_name = "chords"

    dbConnection    = engine.connect()

    # make sure that the database is setup for utf-8
    result = engine.execute(
        text("ALTER DATABASE jazztunes CHARACTER SET utf8 COLLATE utf8_general_ci;")
    )
    print(result)

    try:
        frame = df.to_sql(table_name,
                          dbConnection,
                          index=False,
                          index_label='file_name',
                          if_exists='replace')
    except ValueError as vx:
        print(vx)
    except Exception as ex:
        print(ex)
    else:
        print("Table %s created successfully." % table_name)
    finally:
        result = engine.execute(f"SELECT count(*) FROM {table_name}").fetchall()
        print(result)


if __name__ == "__main__":
    set_pandas_display_options()

    cs = ChordSequence()
    df = cs.generate_sequences()
    df['ChordsDisplay'] = df['Chords'].apply(lambda x: ", ".join(x))

    df_sql = df.drop(columns=['Chords'])

    insert_to_sql(df_sql)

    print(df_sql.head(50))

    #meta = pd.read_csv('02c_tune_sql_import.csv', sep='\t')

    file_name = 'dataset/test3/500 Miles High.xml'
    file_name = 'dataset/test3/Take Five.xml'

    dd = df_sql.query(f'file_name == "{file_name}"')

    ## Write Lead Sheet as a Dictionary which can be used by he Dash DataTable

    # define number of bars per line
    num_bars_per_line = 4

    leadsheet = []
    line = {}

    # generate table content
    for index, row in dd.iterrows():
        # last measure per line
        if row['MeasureNum'] % num_bars_per_line == 0:
            chords = row['ChordsDisplay']
            colname = f"col{row['MeasureNum'] % num_bars_per_line}"
            line[colname] = chords
            leadsheet.append(line)
            line = {}
        else:
            chords = row['ChordsDisplay']
            colname = f"col{row['MeasureNum'] % num_bars_per_line}"
            line[colname] = chords

    print(leadsheet)

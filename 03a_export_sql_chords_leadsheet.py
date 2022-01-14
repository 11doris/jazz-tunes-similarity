from database.api import using_alchemy
from sqlalchemy import text
from chords.ChordSequence import ChordSequence
from dataset.utils import set_pandas_display_options
import pandas as pd
from data_preparation.utils import output_preprocessing_directory


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

    cs = ChordSequence(chord_style='leadsheet')
    df = cs.create_leadsheet_chords()

    meta = pd.read_csv(f'{output_preprocessing_directory}/02c_tune_sql_import.csv', sep='\t')
    meta = meta.loc[:, ['id', 'file_name', 'title']]
    meta = meta.drop_duplicates()

    num_rows = len(df)

    df_sql = df.merge(meta, on='file_name', how='inner')

    # make sure that we did not loose any rows while merging
    assert num_rows == len(df_sql)

    insert_to_sql(df_sql)

    print(df_sql.head(50))

    df_sql.to_csv(f'{output_preprocessing_directory}/03_chords_sql_import.csv', sep='\t', header=True, encoding='utf8')

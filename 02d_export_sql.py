from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import json
import os

"""
This needs a config file with the database connect information, in the style of:
{
  "config": {
	"host"     : "jazztunes.mysql.database.azure.com",
	"user"     : "username",
	"password" : "password",
	"database" : "jazztunes"
  },
  "ssl_args": {
	"ssl_ca"   : "database/DigiCertGlobalRootCA.crt.pem"
  }
}
"""

def using_alchemy():

    filename = "database/db_config.json"
    if not os.path.isfile(filename):
        print(f"ERROR: File {filename} is missing.")
        exit()

    config = json.load(open(filename))

    conn_params_dic = config['config']
    ssl_args = config['ssl_args']

    # Using alchemy method
    connect_alchemy = "mysql+pymysql://%s:%s@%s/%s?charset=utf8" % (
        conn_params_dic['user'],
        conn_params_dic['password'],
        conn_params_dic['host'],
        conn_params_dic['database']
    )

    try:
        print('Connecting to the MySQL...........')
        engine = create_engine(connect_alchemy, connect_args=ssl_args)
        print("Connection successfully..................")
    except SQLAlchemyError as e:
        err=str(e.__dic__['orig'])
        print("Error while connecting to MySQL", err)
        # set the connection to 'None' in case of error
        engine = None
    return engine


if __name__ == '__main__':

    engine = using_alchemy()

    table_name = "tunes"
    df = pd.read_csv('02c_tune_sql_import.csv')

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
                          index_label='Id',
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


    # Just an example to query the data base: retrieve all tunes from Tommy Flanagan
    composer_name = 'Tommy Flanagan'
    print(f'Querying the tunes from {composer_name}:')
    result = engine.execute(
        text(
            f"SELECT title, composer, year \
            FROM {table_name} \
            WHERE composer = '{composer_name}' \
            ORDER BY year;"
        )
    )
    print(f"Found {result.rowcount} rows.")

    #rows = [dict(row) for row in result.fetchall()]
    for row in result.fetchall():
        print(row)

    dbConnection.close()
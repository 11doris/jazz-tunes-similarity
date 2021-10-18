from sqlalchemy import create_engine
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

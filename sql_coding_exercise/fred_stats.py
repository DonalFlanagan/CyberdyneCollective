# -*- coding: utf-8 -*-

#fixme removed redundant args
"""
Retrieve statistics from the FRED api

Usage:
    fred_stats.py --user=USER --password=PASSWORD [--host=HOST] [--api_key=API_KEY] [--database=DATABASE] [--port=PORT]
    fred_stats.py (-h | --help)
    fred_stats.py (-v | --version)

Options:
    -u --user=USER                Your Postgres username.
    -p --password=PASSWORD        Your Postgres password.
    --host=HOST                   Database hostname. Default = 'localhost'.
    -a --api_key=API_KEY          Your FRED api key.
                                  Default = Dónal Flanagan's Fred API key.
    -d --database=DATABASE        The name of the database in which you wish to store the Fred data.
                                  If the database does not exist it will be created. Default = 'fred_db'.
    --port=PORT                   The Postgres port. Default = 5432
    -h --help                     Show this screen.
    -v --version                  Show version.

"""

#fixme: remove redundant imports
import sys
import logging
import re
import psycopg2
import requests
import pandas as pd
from fredapi import Fred
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from docopt import docopt

from pprint import pprint as pp


logger = logging.getLogger('fred_stats')
__version__ = '0.0.1'


def get_db_engine(db_name, user, password, host, port=5432):

    db_connection = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
        database=db_name,
        user=user,
        password=password,
        host=host,
        port=port
    )

    engine = create_engine(db_connection)
    if not database_exists(engine.url):
        try:
            create_database(engine.url)

        except Exception as exc:
            logger.exception('Could not create database. \nException: %r', exc)
            return exc
    return engine


def main():
    args = docopt(__doc__, version='fki-missing-answers %s' % __version__)

    user = args.get('--user')
    password = args.get('--password')
    host = args.get('--host') if args.get('--host') else 'localhost'
    api_key = args.get('--api_key') if args.get('--api_key') else '01af77900eb060649a7c504ee0705b4d'
    db_name = args.get('--database') if args.get('--database') else 'fred_db'
    port = args.get('--port') if args.get('--port') else 5432

    engine = get_db_engine(db_name, user, password, host, port)

    print('\n---------------------------------------')
    print('db created')
    print('---------------------------------------\n')


    try:

        logging.basicConfig(level=logging.DEBUG)
        logger.info('starting fred_stats')

        fred = Fred(api_key=api_key)
        gdp = fred.get_series('GDPC1').rename('gdp')  # ('GDP')
        um_cust_sent_index = fred.get_series('UMCSENT').rename('umcsent')  # ('UM customer sentiment index')
        us_civ_unemploy_rate = fred.get_series('UNRATE').rename('unrate')  # ('US  Civilian Unemployment Rate')

        frames = [gdp, um_cust_sent_index, us_civ_unemploy_rate]
        fred_data = pd.concat(frames, axis=1)

        print('\n---------------------------------------')
        print('data retrieved')
        print('---------------------------------------\n')

        # fixme: add option to replace or append here depending on load type

        fred_data.to_sql(name='fred_data', con=engine, if_exists='replace', index=True, index_label='timestamp')

        print('\n---------------------------------------')
        print('data inserted')
        print('---------------------------------------\n')

        unemployment_query = """
            SELECT EXTRACT(YEAR from timestamp) as year, avg(unrate)
            FROM fred_data
            where timestamp >= '1980-01-01' and timestamp <= '2015-12-31'
            GROUP BY year
            ORDER BY year
        """

        result_set = engine.execute(unemployment_query)


        #for r in result_set:
        #    print(r)





    except KeyboardInterrupt:
        logger.info('Stopping fred_stats')
    except Exception as exc:
        logger.exception('Got exception %r', exc)
        return exc


if __name__ == '__main__':
    sys.exit(main())

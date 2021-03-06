# -*- coding: utf-8 -*-

"""
Retrieve statistics from the FRED api

Usage:
    fred_stats.py --user=USER --password=PASSWORD [--start=START]
                  [--end=END] [--database=DATABASE] [--table=TABLE]
                  [--host=HOST] [--api_key=API_KEY] [--port=PORT]
    fred_stats.py (-h | --help)
    fred_stats.py (-v | --version)

Options:
    -u --user=USER              Your Postgres username.
    -p --password=PASSWORD      Your Postgres password.
    -h --help                   Show this screen.
    -v --version                Show version.

Additional options:
    -s --start=START            yyyy. Start year for average unemployment rate aggregation.
                                Default = 1980
    -e --end=END                yyyy. End year for average unemployment rate aggregation.
                                Default = 2015
    -d --database=DATABASE      The name of the database in which you wish to store the Fred data.
                                If the database does not exist it will be created.
                                Default = 'fred_db'.
    -t --table=TABLE            The name of the table in which you wish to insert/update the data.
                                Default = 'fred_data
    -a --api_key=API_KEY        Your FRED api key.
                                Default = Fred API key of Dónal Flanagan.
    --host=HOST                 Database hostname.
                                Default = 'localhost'.
    --port=PORT                 The Postgres port.
                                Default = 5432
"""

import sys
import logging
import pandas as pd
from fredapi import Fred
from sqlalchemy import create_engine, text, Table, Column, DateTime, Numeric, MetaData
from sqlalchemy_utils import database_exists, create_database
from docopt import docopt


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
            logger.info('Database created: %s', db_name)
            create_database(engine.url)

        except Exception as exc:
            logger.exception('Could not create database. \nException: %r', exc)
            return exc
    return engine


class FredStats:
    def __init__(self, api_key):
        self.fred = Fred(api_key=api_key)

    def retrieve_stats(self, series_names):
        # Retrieve the data from the FRED api
        frames = []
        for series_name in series_names:
            data_series = self.fred.get_series(series_name).rename(series_name)
            frames.append(data_series)

        data = pd.concat(frames, axis=1)
        return data


class DatabaseInterface:
    def __init__(self, ):

        # If the table does not already exist, create it.
        metadata = MetaData(engine)
        fred_table = Table(table_name,
                           metadata,
                           Column('timestamp', DateTime),
                           Column('gdp', Numeric),
                           Column('umcsent', Numeric),
                           Column('unrate', Numeric))
        if not engine.dialect.has_table(engine, table_name):
            metadata.create_all()


        # Insert the data
        conn = engine.connect()
        for index, row in fred_data.iterrows():
            ins = fred_table.insert().values(timestamp=index, gdp=row[0], umcsent=row[1], unrate=row[2])
            conn.execute(ins)


def main():

    args = docopt(__doc__, version='fred_stats %s' % __version__)

    api_key = args.get('--api_key') if args.get('--api_key') else '01af77900eb060649a7c504ee0705b4d'
    start_year = args.get('--start') if args.get('--start') else '1980'
    end_year = args.get('--end') if args.get('--end') else '2015'

    start_date = '{start_year}-01-01'.format(start_year=start_year)
    end_date = '{end_year}-12-31'.format(end_year=end_year)

    series_names = ['GDPC1', 'UMCSENT', 'UNRATE']

    try:
        logging.basicConfig(level=logging.DEBUG)
        logger.info('starting fred_stats')

        fred_stats = FredStats(api_key=api_key)
        data = fred_stats.retrieve_stats(series_names=series_names)
        print(data)






    except KeyboardInterrupt:
        logger.info('Stopping fred_stats')
    except Exception as exc:
        logger.exception('Got exception %r', exc)
        return exc

if __name__ == '__main__':
    sys.exit(main())

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
from time import time

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


def main():
    args = docopt(__doc__, version='fred_stats %s' % __version__)

    user = args.get('--user')
    password = args.get('--password')
    host = args.get('--host') if args.get('--host') else 'localhost'
    api_key = args.get('--api_key') if args.get('--api_key') else '01af77900eb060649a7c504ee0705b4d'
    db_name = args.get('--database') if args.get('--database') else 'fred_db'
    table_name = args.get('--table') if args.get('--table') else 'fred_data'
    port = int(args.get('--port')) if args.get('--port') else 5432
    start_year = args.get('--start') if args.get('--start') else '1980'
    end_year = args.get('--end') if args.get('--end') else '2015'

    start_date = '{start_year}-01-01'.format(start_year=start_year)
    end_date = '{end_year}-12-31'.format(end_year=end_year)

    # Instantiate the sqlalchemy database interface
    engine = get_db_engine(db_name, user, password, host, port)

    try:
        logging.basicConfig(level=logging.DEBUG)
        logger.info('starting fred_stats')

        # Retrieve the data from the FRED api
        fred = Fred(api_key=api_key)
        gdp = fred.get_series('GDPC1').rename('gdp')
        um_cust_sent_index = fred.get_series('UMCSENT').rename('umcsent')
        us_civ_unemploy_rate = fred.get_series('UNRATE').rename('unrate')

        frames = [gdp, um_cust_sent_index, us_civ_unemploy_rate]
        fred_data = pd.concat(frames, axis=1)

        t1 = time()
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

        t2 = time()
        print('time:', t2 - t1)

        # Query the SQL table for the average unemployment rate.
        unemployment_query = """SELECT Extract(YEAR from timestamp)::INT as year, avg(unrate)
                                FROM {t_name}
                                WHERE timestamp >= :start_date and timestamp <= :end_date
                                GROUP BY year
                                ORDER BY year;""".format(t_name=table_name)

        result = engine.execute(text(unemployment_query), start_date=start_date, end_date=end_date)

        df = pd.DataFrame(result.fetchall())
        df.columns = result.keys()
        df.set_index('year', inplace=True)

        print('The average rate of unemployment in the USA for each year between %s and %s is as follows:' %
              (start_date, end_date))
        print(df)

    except KeyboardInterrupt:
        logger.info('Stopping fred_stats')
    except Exception as exc:
        logger.exception('Got exception %r', exc)
        return exc

if __name__ == '__main__':
    sys.exit(main())

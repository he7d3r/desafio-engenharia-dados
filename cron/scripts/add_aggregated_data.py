#!/usr/bin/env python

"""Add tables with aggregated data for ease of consumption

Usage:
    add_aggregated_data [--db=<path>] [--table=<name>] [--year=<int>]
                        [--more-data]
    add_aggregated_data -h | --help

Options:
    -h --help                 Show this screen.
    --db=<path>               The path to a file for the database
    --table=<name>            The name for a table in the database
    --year=<int>              The year whose data should be aggregated
    --more-data               Add data to the tables 'top_by_state_and_month'
                              and  'state_contributions'
"""
import docopt
import os.path
import pandas as pd
from sqlalchemy import create_engine


def main(argv=None):
    global engine

    args = docopt.docopt(__doc__, argv=argv)

    db_path = os.path.expanduser(args['--db'])
    engine = create_engine('sqlite:///{}'.format(db_path))

    table = args['--table']
    year = args['--year']

    add_top_by_state_and_year_from(table, year)
    if args['--more-data']:
        add_top_by_state_and_month_from(table, year)
        add_state_contributions_from(table, year)


def add_top_by_state_and_year_from(table, year, n=3):
    '''
    Add table with top n products with highest total traded value in the
    specified year, by state.
    '''

    query = f'''
    WITH totals AS
      (SELECT federative_unit,
              year,
              product,
              total,
              ROW_NUMBER() OVER(PARTITION BY federative_unit
                                ORDER BY total DESC) AS position
       FROM
         (SELECT SG_UF_NCM federative_unit,
                 strftime("%Y", s.DATA) year,
                 s.CO_NCM product,
                 SUM(VL_FOB) total
          FROM {table} s
          WHERE year = "{year}"
          GROUP BY federative_unit,
                   product))
    SELECT t.federative_unit,
           t.year,
           t.product,
           t.total
    FROM totals t
    WHERE t.position <= 3
    ORDER BY t.federative_unit,
             t.year,
             t.total DESC
    '''
    print(f'Adding top products by state from {table} ({year}).')
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
        df['kind'] = table
        df.to_sql('top_by_state_and_year', engine, if_exists='append',
                  index=False)


def add_top_by_state_and_month_from(table, year, n=3):
    '''
    Add table with top n products with highest total traded value in the
    specified year, by month, by state.
    '''

    query = f'''
    WITH totals AS
      (SELECT federative_unit,
              year,
              month,
              product,
              total,
              ROW_NUMBER() OVER(PARTITION BY federative_unit, month
                                ORDER BY total DESC) AS position
       FROM
         (SELECT SG_UF_NCM federative_unit,
                 strftime("%Y", s.DATA) year,
                 ltrim(strftime("%m", s.DATA), "0") month,
                 s.CO_NCM product,
                 SUM(VL_FOB) total
          FROM {table} s
          WHERE year = "{year}"
          GROUP BY month,
                   federative_unit,
                   product))
    SELECT t.federative_unit,
           t.year,
           t.month,
           t.product,
           t.total
    FROM totals t
    WHERE t.position <= 3
    ORDER BY t.federative_unit,
             t.month,
             t.total DESC
    '''
    print(f'Adding top products by state and month from {table} ({year}).')
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
        df['kind'] = table
        df.to_sql('top_by_state_and_month', engine, if_exists='append',
                  index=False)


def add_state_contributions_from(table, year):
    '''
    Add table with the percentage of contribution of each state to the
    country's total transactions in the given year.
    '''

    query = f'''
    SELECT strftime("%Y", t.DATA) year,
                                  SG_UF_NCM federative_unit,
                                  SUM(VL_FOB) total,
                                  100.0 * SUM(VL_FOB) /
      (SELECT SUM(VL_FOB)
       FROM {table}
       WHERE strftime("%Y", DATA) = "{year}") percentage
    FROM {table} t
    WHERE year="{year}"
    GROUP BY SG_UF_NCM
    ORDER BY total DESC
    '''
    print(f'Adding state contributions from {table} ({year}).')
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
        df['kind'] = table
        df.to_sql('state_contributions', engine, if_exists='append',
                  index=False)


if __name__ == '__main__':
    main()

#!/usr/bin/env python

"""Creates an sqlite database and add data from CSV files.

Usage:
    create_db <csv-file>... [--db=<path>] [--table=<name>] [--encoding=<code>]
    create_db -h | --help

Options:
    -h --help           Show this screen.
    <csv-file>          A CSV file to process
    --db=<path>         The path to a file for the database
    --table=<name>      The name for a table in the database
    --encoding=<name>   The encoding used in the CSV file. E.g.: ISO-8859-1
"""
import docopt
import os.path
import pandas as pd
from sqlalchemy import create_engine


def main(argv=None):
    global engine

    args = docopt.docopt(__doc__, argv=argv)
    csv_paths = args['<csv-file>']

    db_path = os.path.expanduser(args['--db'])
    engine = create_engine('sqlite:///{}'.format(db_path))

    table = args['--table']
    encoding = args['--encoding']

    add_full_data(csv_paths, table, encoding=encoding)


def replace_year_month_by_date(df, year_col='year', month_col='month',
                               date_col='date'):
    '''
    Replace year and month columns by a date column

    Parameters:
        df: (pandas.core.frame.DataFrame): Dataframe containing a year column
        and a month column.
            Example:
                year month ...
            1   2017     3 ...
            2   2018    12 ...

        year_col: (str) The name of the column containing the year
        month_col: (str) The name of the column containing the month
        date_col: (str) The name of the column which will contain the date

    Returns:
        df: (pandas.core.frame.DataFrame): Dataframe with a new date column,
            and without the old year and month columns.
            Example:
            ...       date
            1 ... 2017-03-01
            2 ... 2018-12-01
    '''
    df[date_col] = pd.to_datetime(
        df[year_col].astype(str) + df[month_col].astype(str), format='%Y%m')
    assert ((df[date_col].dt.year == df[year_col]).all()
            and (df[date_col].dt.month == df[month_col]).all())
    return df.drop([year_col, month_col], axis=1)


def add_full_data(csv_paths, table, encoding=None):
    '''
    Add all data from CSV files to database tables
    '''
    chunk_size = 500000
    for csv_path in csv_paths:
        print(f'Processing {csv_path}')
        chunks = pd.read_csv(
            csv_path,
            delimiter=';',
            chunksize=chunk_size,
            encoding=encoding)
        for chunk in chunks:
            if table in ['import', 'export']:
                chunk = replace_year_month_by_date(chunk, year_col='CO_ANO',
                                                   month_col='CO_MES',
                                                   date_col='DATA')
            elif table not in ['ncm', 'uf']:
                err_msg = (f'Unknown value for "table": {table}. '
                           'Must be one of "import", "export", "ncm" or "uf".')
                raise ValueError(err_msg)
            chunk.to_sql(table, engine, if_exists='append', index=False)
    print('Done.')


if __name__ == '__main__':
    main()

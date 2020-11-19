#!/usr/bin/env python

"""Add data from CSV files to the database.

Usage:
    add_data <csv-file>... [--db=<path>] [--table=<name>] [--encoding=<code>]
    add_data -h | --help

Options:
    -h --help           Show this screen.
    <csv-file>          A CSV file to process
    --db=<path>         The url for the database
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

    engine = create_engine(os.path.expanduser(args['--db']))

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


def fix_non_integers(df):
    '''
    Replace non integer values by fake values

    Parameters:
        df: (pandas.core.frame.DataFrame): Dataframe whose columns will be
            fixed

    Returns:
        df: (pandas.core.frame.DataFrame): Dataframe with the replacements
            applied
    '''
    df['CO_CUCI_ITEM'] = df['CO_CUCI_ITEM']\
        .replace('II', 2).replace('I', 1).astype(int)
    df['CO_EXP_SUBSET'] = df['CO_EXP_SUBSET'].fillna(0).astype(int)
    return df


def add_full_data(csv_paths, table, encoding=None):
    '''
    Add all data from CSV files to database tables
    '''
    chunk_size = 200000
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
            elif table == 'ncm':
                chunk = fix_non_integers(chunk)
            elif table != 'uf':
                err_msg = (f'Unknown value for "table": {table}. '
                           'Must be one of "import", "export", "ncm" or "uf".')
                raise ValueError(err_msg)
            chunk.to_sql(table, engine, if_exists='append', index=False)
    print('Done.')


if __name__ == '__main__':
    main()

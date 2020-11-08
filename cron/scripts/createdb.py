#!/usr/bin/env python

"""Creates an sqlite database with the data from CSV files.

Usage:
    createdb <csv-file>... [--db=<path>] [--table=<name>] [--encoding=<code>]
    createdb -h | --help

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
    args = docopt.docopt(__doc__, argv=argv)
    csv_paths = args['<csv-file>']
    db_path = os.path.expanduser(args['--db'])
    table = args['--table']
    encoding = args['--encoding']

    run(csv_paths, db_path, table, encoding=encoding)


def replace_year_month_by_date(df):
    date_parts = {'CO_ANO': 'year', 'CO_MES': 'month'}
    df['DATA'] = pd.to_datetime(
        df[date_parts.keys()].assign(day=1).rename(columns=date_parts)
    )
    df = df.drop(date_parts.keys(), axis=1)
    return df


def run(csv_paths, db_path, table, encoding=None):
    eng = create_engine('sqlite:///{}'.format(db_path))
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
                chunk = replace_year_month_by_date(chunk)
            elif table not in ['ncm', 'uf']:
                err_msg = (f'Unknown value for "table": {table}. '
                           'Must be one of "import", "export", "ncm" or "uf".')
                raise ValueError(err_msg)
            chunk.to_sql(table, eng, if_exists='append', index=False)
    print('Done.')


if __name__ == '__main__':
    main()

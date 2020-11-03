#!/usr/bin/env python

"""Creates an sqlite database with the data from CSV files.

Usage:
    createdb <csv-file>... [--db=<path>] [--table=<name>]
    createdb -h | --help

Options:
    -h --help           Show this screen.
    <csv-file>          A CSV file to process
    --db=<path>         The path to a file for the database
    --table=<name>      The name for a table in the database
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

    run(csv_paths, db_path, table)


def run(csv_paths, db_path, table):
    eng = create_engine('sqlite:///{}'.format(db_path))
    conn = eng.connect()
    chunk_size=500000
    for csv_path in csv_paths:
        print('Processing {}'.format(csv_path))
        try:
            for chunk in pd.read_csv(csv_path, delimiter=';', chunksize=chunk_size):
                chunk.to_sql(table, eng, if_exists='append')
        except UnicodeDecodeError:
            for chunk in pd.read_csv(csv_path, delimiter=';', chunksize=chunk_size, encoding = 'ISO-8859-1'):
                chunk.to_sql(table, eng, if_exists='append')

if __name__ == '__main__':
    main()

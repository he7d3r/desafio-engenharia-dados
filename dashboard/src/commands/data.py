import click
import pandas as pd
from flask.cli import AppGroup
from src.database import db


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


def init_app(app):
    data_cli = AppGroup('data',
                        short_help='Commands to populate the database tables')

    @data_cli.command()
    @click.argument('csv_paths', type=click.Path(exists=True), nargs=-1)
    @click.option(
        '--table',
        type=click.Choice(['import', 'export', 'ncm', 'ncm', 'uf']),
        help='The name for a table in the database',
        required=True
    )
    @click.option('--encoding', default=None, show_default=True)
    @click.option('--chunk_size', default=200000, show_default=True)
    def add(csv_paths, table, encoding, chunk_size):
        '''
        Add all data from CSV files to database table
        '''
        for csv_path in csv_paths:
            click.echo(f'Processing {csv_path}')
            chunks = pd.read_csv(
                csv_path,
                delimiter=';',
                chunksize=chunk_size,
                encoding=encoding)
            for chunk in chunks:
                if table in ['import', 'export']:
                    chunk = replace_year_month_by_date(
                        chunk,
                        year_col='CO_ANO',
                        month_col='CO_MES',
                        date_col='DATA'
                    )
                elif table == 'ncm':
                    chunk = fix_non_integers(chunk)
                chunk.to_sql(table, db.engine, if_exists='append',
                             index=False)
        click.echo(f'Finished adding data to table "{table}".')

    @data_cli.command()
    @click.option(
        '--table',
        type=click.Choice(['import', 'export']),
        help='The name of a table in the database, corresponding to the kind' +
             ' of trade of interest',
        required=True
    )
    @click.option(
        '--year',
        type=int,
        required=True,
        help='The year whose data should be aggregated')
    @click.option(
        '--n',
        default=3,
        show_default=True,
        help='How many of the top products to return for each state')
    def aggregate_by_state(table, year, n=3):
        '''
        Add table with top n products with highest total traded value in the
        specified year, by state, for the kind of trade specified by the table
        name.
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
        WHERE t.position <= {n}
        ORDER BY t.federative_unit,
                t.year,
                t.total DESC
        '''
        with db.engine.connect() as connection:
            df = pd.read_sql(query, connection)
            df['kind'] = table
            df.to_sql('top_by_state_and_year', db.engine, if_exists='append',
                      index=False)
        click.echo(
            f'Finished adding top products by state from {table} ({year}).'
        )

    @data_cli.command()
    @click.option(
        '--table',
        type=click.Choice(['import', 'export']),
        help='The name of a table in the database',
        required=True
    )
    @click.option(
        '--year',
        type=int,
        required=True,
        help='The year whose data should be aggregated')
    @click.option(
        '--n',
        default=3,
        show_default=True,
        help='How many of the top products to return for each month and state')
    def aggregate_by_month_and_state(table, year, n):
        '''
        Add table with top n products with highest total traded value in the
        specified year, by month, by state, for the kind of trade specified by
        the table name.
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
        WHERE t.position <= {n}
        ORDER BY t.federative_unit,
                t.month,
                t.total DESC
        '''
        with db.engine.connect() as connection:
            df = pd.read_sql(query, connection)
            df['kind'] = table
            df.to_sql('top_by_state_and_month', db.engine, if_exists='append',
                      index=False)
        click.echo(
            'Finished adding top products by state and month from ' +
            f'{table} ({year}).'
        )

    @data_cli.command()
    @click.option(
        '--table',
        type=click.Choice(['import', 'export']),
        help='The name of a table in the database',
        required=True
    )
    @click.option(
        '--year',
        type=int,
        required=True,
        help='The year whose data should be aggregated')
    def aggregate_state_contributions(table, year):
        '''
        Add table with the percentage of contribution of each state to the
        country's total transactions in the given year, for the kind of trade
        specified by the table name.
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
        with db.engine.connect() as connection:
            df = pd.read_sql(query, connection)
            df['kind'] = table
            df.to_sql('state_contributions', db.engine, if_exists='append',
                      index=False)
        click.echo(
            f'Finished adding state contributions from {table} ({year}).'
        )

    app.cli.add_command(data_cli)

import click
import pandas as pd
from flask.cli import AppGroup
from src.database import db


def get_states(csv_path):
    '''
    Read the relevant state columns from specified CSV file
    '''
    df = pd.read_csv(csv_path, delimiter=';', encoding='ISO-8859-1',
                     usecols=['SG_UF', 'NO_UF'])
    return df.rename(columns={'SG_UF': 'state_code', 'NO_UF': 'state'})


def get_products(csv_path):
    '''
    Read the relevant product columns from specified CSV file
    '''
    df = pd.read_csv(csv_path, delimiter=';', encoding='ISO-8859-1',
                     usecols=['CO_NCM', 'NO_NCM_POR'])
    return df.rename(columns={'CO_NCM': 'product_code',
                              'NO_NCM_POR': 'product'})


def init_app(app):
    data_cli = AppGroup('data',
                        short_help='Commands to populate the database tables')

    @data_cli.command()
    @click.argument('csv_path', type=click.Path(exists=True), nargs=1)
    @click.argument('states_path', type=click.Path(exists=True), nargs=1)
    @click.argument('products_path', type=click.Path(exists=True), nargs=1)
    @click.option(
        '--kind',
        type=click.Choice(['import', 'export']),
        help='The kind of trade being processed',
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
    def aggregate_by_state_and_add(csv_path, states_path, products_path,
                                   kind, year, n=3):
        '''
        Process the specified CSV files to generate a table with the top n
        products with highest total traded value in the specified year, by
        state, for the kind of trade specified.
        '''
        click.echo(f'Processing {csv_path}...')
        df = pd.read_csv(csv_path, delimiter=';',
                         usecols=['CO_ANO', 'CO_NCM', 'SG_UF_NCM', 'VL_FOB'])
        df.columns = ['year', 'product_code', 'state_code', 'total']
        df = df[df['year'] == year]
        # Compute the totals for each combination of state and product
        totals = df.groupby(['state_code', 'product_code'])[['total']].sum()
        # Rank the products of each state by their total values
        ranked = totals.assign(
            rank=totals.sort_values(['total'], ascending=False)
            .groupby(['state_code'])
            .cumcount() + 1
        )
        # Keep only the wanted number of products for each state
        top = (ranked.query(f'rank <= {n}')
               .sort_values(['state_code', 'rank'])
               .drop('rank', axis=1)
               ).reset_index()
        # Add columns for the year and kind of trade being processed
        top = top.assign(year=year, kind=kind)

        # JOIN metadata
        states = get_states(states_path)
        products = get_products(products_path)
        merged_top = top.merge(states, on='state_code')\
            .merge(products, on='product_code')
        merged_top.to_sql('top_by_state_and_year', db.engine, index=False,
                          if_exists='append')
        click.echo(f'Finished ranking of products {kind}ed in {year} ' +
                   'by state.')

    @data_cli.command()
    @click.argument('csv_path', type=click.Path(exists=True), nargs=1)
    @click.argument('states_path', type=click.Path(exists=True), nargs=1)
    @click.argument('products_path', type=click.Path(exists=True), nargs=1)
    @click.option(
        '--kind',
        type=click.Choice(['import', 'export']),
        help='The kind of trade being processed',
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
        help='How many of the top products to return for each state and month')
    def aggregate_by_month_and_state_and_add(csv_path, states_path,
                                             products_path, kind, year, n=3):
        '''
        Process the specified CSV files to generate a table with the top n
        products with highest total traded value in the specified year, by
        month and state, for the kind of trade specified.
        '''
        click.echo(f'Processing {csv_path}...')
        df = pd.read_csv(csv_path, delimiter=';',
                         usecols=['CO_ANO', 'CO_MES', 'CO_NCM', 'SG_UF_NCM',
                                  'VL_FOB'])
        df.columns = ['year', 'month', 'product_code', 'state_code', 'total']
        df = df[df['year'] == year]
        # Compute the totals for each combination of state, month and product
        totals = df.groupby(
            ['month', 'state_code', 'product_code'])[['total']].sum()
        # Rank the products of each state and month by their total values
        ranked = totals.assign(
            rank=totals.sort_values(['total'], ascending=False)
            .groupby(['month', 'state_code'])
            .cumcount() + 1
        )
        # Keep only the wanted number of products for each state and month
        top = (ranked.query(f'rank <= {n}')
               .sort_values(['state_code', 'month', 'rank'])
               .drop('rank', axis=1)
               ).reset_index()
        # Add columns for the year and kind of trade being processed
        top = top.assign(year=year, kind=kind)

        # JOIN metadata
        states = get_states(states_path)
        products = get_products(products_path)
        merged_top = top.merge(states, on='state_code')\
            .merge(products, on='product_code')
        merged_top.to_sql('top_by_state_and_month', db.engine, index=False,
                          if_exists='append')
        click.echo(f'Finished ranking of products {kind}ed in {year} ' +
                   'by month and state.')

    @data_cli.command()
    @click.argument('csv_path', type=click.Path(exists=True), nargs=1)
    @click.argument('states_path', type=click.Path(exists=True), nargs=1)
    @click.option(
        '--kind',
        type=click.Choice(['import', 'export']),
        help='The kind of trade being processed',
        required=True
    )
    @click.option(
        '--year',
        type=int,
        required=True,
        help='The year whose data should be aggregated')
    def aggregate_state_contributions_and_add(csv_path, states_path,
                                              kind, year):
        '''
        Process the CSV file specified to generate a table with the percentage
        of contribution of each state to the country's total transactions in
        the given year, for the kind of trade specified.
        '''
        click.echo(f'Processing {csv_path}...')
        df = pd.read_csv(csv_path, delimiter=';',
                         usecols=['CO_ANO', 'SG_UF_NCM', 'VL_FOB'])
        df.columns = ['year', 'state_code', 'total']
        df = df[df['year'] == year]
        year_total = df['total'].sum()
        state_contribs = df.groupby(
            ['state_code'], as_index=False)['total'].sum()
        state_contribs['year'] = year
        state_contribs['kind'] = kind
        state_contribs['percentage'] = \
            100.0 * state_contribs['total'] / year_total

        # JOIN metadata
        states = get_states(states_path)
        merged_state_contribs = state_contribs\
            .merge(states, on='state_code')
        merged_state_contribs.to_sql('state_contributions', db.engine,
                                     index=False, if_exists='append')
        click.echo('Finished aggregation of states contributions to the ' +
                   f'{kind}s in {year}.')

    app.cli.add_command(data_cli)

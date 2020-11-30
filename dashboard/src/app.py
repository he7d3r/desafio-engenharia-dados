import base64
import io
from datetime import datetime
from textwrap import fill

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from flask import Flask, render_template
from matplotlib.backends.backend_agg import FigureCanvasAgg

from src import commands, database
from src.config import config


def get_available_state_codes():
    """
    Get states' codes and names from DB and return them as a dataframe
    """
    with database.db.engine.connect() as connection:
        query = '''
        SELECT DISTINCT(state_code) state_code,
               state
        FROM state_contributions
        WHERE state_code IN ('AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES',
                             'GO', 'MA', 'MT', 'MS', 'MG', 'PR', 'PB', 'PA',
                             'PE', 'PI', 'RN', 'RS', 'RJ', 'RO', 'RR', 'SC',
                             'SE', 'SP', 'TO')
        ORDER BY state
        '''
        return pd.read_sql(query, connection, index_col='state_code')


def get_available_years():
    """
    Get the years which are present in the DB and return them as a list of
    integers.
    """
    with database.db.engine.connect() as connection:
        query = '''
        SELECT DISTINCT(year)
        FROM top_by_state_and_year
        ORDER BY year
        '''
        return pd.read_sql(query, connection).year.astype(int).values.tolist()


def get_month_name(month):
    """
    Get the month name in Portuguese.

    Parameters:
        month: (int): The month number from 1 to 12

    Returns:
        name: (str): The name of the month in Portuguese, or
        'todos os meses' (all months) if month is not in the range from 1 to 12
    """
    names = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    if month in names:
        return names[month]
    return 'todos os meses'


def get_month_options(year):
    """
    Get the month options for the given year.

    For the previous year, there is data available for each individual month.
    However, for previous years only the aggregate statistics is available.

    Parameters:
        year: (int): The year for which the months will be listed.
    """
    previous_year = datetime.now().year - 1
    if year == previous_year:
        return list(range(1, 13))
    return []


def get_top_products(kind, state, year, month, count=3, index=None):
    """
    Get products with the largest FOB values in USD and return them as a
    dataframe.

    Parameters:
        kind: (str): The kind of trade. One of 'import' or 'export'.
        state: (str): The UF code of the state of origin/destiny the trade
        year: (str): The year of the trade
        count: (int): How many products to get
    """
    if month:
        table = 'top_by_state_and_month'
        period_filter = f't.year=\'{year}\' AND t.month=\'{month}\''
    else:
        table = 'top_by_state_and_year'
        period_filter = f't.year=\'{year}\''

    query = f'''
    SELECT t.product, t.state, t.total
    FROM {table} t
    WHERE {period_filter}
        AND t.state_code='{state}'
        AND t.kind='{kind}'
    ORDER BY t.total
    LIMIT {count}
    '''
    with database.db.engine.connect() as connection:
        return pd.read_sql(query, connection, index_col=index)\
                .sort_values('total')


def get_top_contributions(kind, year, limit=3, index=None):
    """
    Get states with largest contributions to the yearly total and return them
    as a dataframe.

    Parameters:
        kind: (str): The kind of trade. One of 'import' or 'export'.
        year: (str): The year of the trades
        limit: (int): Limit the results to this many states.
    """
    limit = f'LIMIT {limit}' if limit is not None else ''

    query = f'''
    SELECT s.state_code, s.state, s.total, s.percentage
    FROM state_contributions s
    WHERE year = '{year}'
      AND kind = '{kind}'
    ORDER BY s.percentage DESC
    {limit}
    '''
    with database.db.engine.connect() as connection:
        return pd.read_sql(query, connection, index_col=index)\
                .sort_values('total')


def large_num_formatter(num, pos=None):
    """
    Format large numbers using appropriate sufixes for powers of 1000

    Parameters:
        num: (int): The tick value to be formatted
        pos: (int): Position of the ticker
    """
    for unit in ['', 'mil', 'Mi.', 'Bi.']:
        if abs(num) < 1000.0:
            return "%3.1f %s" % (num, unit)
        num /= 1000.0
    return "%.1f %s" % (num, 'Tri.')


def get_data_url(fig):
    '''
    Generate a data url using the base 64 encoding of the figure
    '''
    png_image = io.BytesIO()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(png_image)

    png_image_in_base_64 = 'data:image/png;base64,{}'.format(
        base64.b64encode(png_image.getvalue()).decode('utf8')
    )

    return png_image_in_base_64


def get_contribution_plot(df, state, title=None):
    """
    Make a pie chart of the percentage of contribution of each state

    Parameters:
        df: (pandas.core.frame.DataFrame): Dataframe to be plotted
        state: (str): The code of the state
    """
    threshold = 3

    def pct_format(percent, skip_small_values=True):
        if percent <= threshold and skip_small_values:
            return ''
        return '%1.1f%%' % percent

    # Highlight the current state
    explode = [0.03 if code != state else 0.2 for code in df.state_code]
    colors = ['#CCC' if code != state else '#66F'
              for code in df.state_code]

    # Hide the percentages of small contributions, unless it is for the
    # current state. In that case, show it as part of the label, since it would
    # not fit inside its slice.
    labels = [name if df['percentage'][name] > threshold else
              name + ' ({})'.format(
                  pct_format(df['percentage'][name],
                             skip_small_values=False)
                            ) if df['state_code'][name] == state
              else '' for name in df.index]

    fig, ax = plt.subplots()
    ax.pie(df.total, colors=colors, autopct=pct_format, startangle=90,
           explode=explode, labels=labels)
    if title:
        ax.set_title(title, pad=20)
    plt.tight_layout()
    return get_data_url(fig)


def get_plot(df, ylabel='Produto', title=None):
    """
    Make a horizontal bar plot of the dataframe.

    Parameters:
        df: (pandas.core.frame.DataFrame): Dataframe to be plotted
        title: (str): Text to be used as title for the plot
    """
    fig, ax = plt.subplots(figsize=(10, len(df)*0.5 + 1.5))

    df.plot(kind='barh', ax=ax, legend=False)
    for container in ax.containers:
        plt.setp(container, height=0.5)
    for i, v in enumerate(df['total']):
        ax.text(v, i, str(large_num_formatter(v)), color='blue', va='center',
                fontweight='bold')

    if title:
        ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Valor total anual (US$)')

    ax.set_yticklabels([fill(p, 50) for p in df.index])
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(large_num_formatter))

    plt.tight_layout()
    return get_data_url(fig)


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from src import model
    database.init_app(app)
    commands.init_app(app)

    @app.route('/')
    @app.route('/dashboard')
    @app.route('/dashboard/')
    @app.route('/dashboard/<string:state_code>/<int:year>')
    @app.route('/dashboard/<string:state_code>/<int:year>/<int:month>')
    def dashboard(state_code=None, year=None, month=None):
        """
        Show statistics about imports and exports for the state and year
        provided in the URL.

        Parameters:
            state_code: (str): The code of the state of origin/destiny the
                               trade (default the first state available).
            year: (int): The year of the trade (default the first year
                         available).
        """
        previous_year = datetime.now().year - 1
        available_state_codes = get_available_state_codes()
        if state_code is None:
            # Use a large state as default
            if 'SP' in available_state_codes.index:
                state_code = 'SP'
            else:
                state_code = str(available_state_codes.index[0])
        if state_code in available_state_codes.index:
            state_name = available_state_codes['state'][state_code]
            available_years = get_available_years()
            if year is None:
                year = previous_year
            if year in available_years:
                month_options = get_month_options(year)

                if month_options and month in month_options:
                    month_name = get_month_name(month)
                else:
                    month = None
                    month_name = 'todos os meses'

                if month is None and year == previous_year:
                    group = f'({year})'
                    img_top_importers = get_plot(
                        get_top_contributions('import', year, index='state'),
                        ylabel='Estado',
                        title=f'Maiores importadores {group}'
                    )
                    img_top_exporters = get_plot(
                        get_top_contributions('export', year, index='state'),
                        ylabel='Estado',
                        title=f'Maiores exportadores {group}'
                    )
                    img_contribution_to_imports = get_contribution_plot(
                        get_top_contributions('import', year, limit=None,
                                              index='state'),
                        state=state_code,
                        title='Representatividade das importações do estado no'
                        + ' ano\nem relação ao total de importações do país'
                    )
                    img_contribution_to_exports = get_contribution_plot(
                        get_top_contributions('export', year, limit=None,
                                              index='state'),
                        state=state_code,
                        title='Representatividade das exportações do estado no'
                        + ' ano\nem relação ao total de exportações do país'
                    )
                else:
                    img_top_importers = None
                    img_top_exporters = None
                    img_contribution_to_imports = None
                    img_contribution_to_exports = None

                group = f'({state_name}, {month_name} de {year})'
                img_top_imports = get_plot(
                    get_top_products('import', state_code, year, month,
                                     index='product'),
                    ylabel='Produto',
                    title=f'Produtos mais importados {group}'
                )
                img_top_exports = get_plot(
                    get_top_products('export', state_code, year, month,
                                     index='product'),
                    ylabel='Produto',
                    title=f'Produtos mais exportados {group}'
                )
                return render_template(
                    'dashboard.html',
                    month_options=[None] + month_options,
                    month=month,
                    get_month_name=get_month_name,
                    available_years=available_years,
                    year=year,
                    previous_year=previous_year,
                    available_state_codes=available_state_codes,
                    state_code=state_code,
                    img_top_imports=img_top_imports,
                    img_top_exports=img_top_exports,
                    img_top_importers=img_top_importers,
                    img_top_exporters=img_top_exporters,
                    img_contribution_to_imports=img_contribution_to_imports,
                    img_contribution_to_exports=img_contribution_to_exports
                )
        return 'Parâmetro(s) inválido(s).'

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app

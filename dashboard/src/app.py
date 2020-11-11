from flask import Flask, render_template
from sqlalchemy import create_engine
from textwrap import fill
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg
from datetime import datetime

app = Flask(__name__)

DATABASE_URI = 'sqlite:////data/trades.db'
engine = create_engine(DATABASE_URI)


def get_available_federative_units():
    """
    Get states' codes and names from DB and return them as a dataframe
    """
    with engine.connect() as connection:
        query = '''
        SELECT DISTINCT(SG_UF) code,
               NO_UF name
        FROM uf
        WHERE code IN ("AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
                       "MA", "MT", "MS", "MG", "PR", "PB", "PA", "PE", "PI",
                       "RN", "RS", "RJ", "RO", "RR", "SC", "SE", "SP", "TO")
        ORDER BY name
        '''
        return pd.read_sql(query, connection, index_col='code')


def get_available_years():
    """
    Get the years which are present in the DB and return them as a list of
    integers.
    """
    with engine.connect() as connection:
        query = '''
        SELECT DISTINCT(strftime("%Y", DATA)) year
        FROM export
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
        'todos os meses' (all months) if month is None
    """
    names = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    if month in names:
        return names[month]
    elif month is None:
        return 'todos os meses'


def get_month_options(year):
    """
    Get the month options for the given year.

    For the last year, there is data available for each individual month.
    However, for previous years only the aggregate statistics is available.

    Parameters:
        year: (int): The year for which the months will be listed.
    """
    last_year = datetime.now().year - 1
    if year == last_year:
        return list(range(1, 13))
    else:
        return []


def get_top(kind, state, year, month, count=3):
    """
    Get products with the largest FOB values in USD and return them as a
    dataframe.

    Parameters:
        kind: (str): The kind of trade. One of 'import' or 'export'.
        state: (str): The UF code of the state of origin/destiny the trade
        year: (str): The year of the trade
        count: (int): How many items to get
    """
    if month:
        table = 'top_by_state_and_month'
        period_filter = f't.year="{year}" AND t.month="{month}"'
    else:
        table = 'top_by_state_and_year'
        period_filter = f't.year="{year}"'

    query = f'''
    SELECT n.NO_NCM_POR product_name,
        u.NO_UF federative_unit_name,
        t.total
    FROM {table} t
    JOIN uf u ON t.federative_unit=u.SG_UF
    JOIN ncm n ON t.product=n.CO_NCM
    WHERE {period_filter}
        AND t.federative_unit="{state}"
        AND t.kind="{kind}"
    GROUP BY t.product
    ORDER BY t.total
    LIMIT {count}
    '''
    with engine.connect() as connection:
        return pd.read_sql(query, connection)


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


def get_plot(df, title=None):
    """
    Make a horizontal bar plot of the dataframe.

    Parameters:
        df: (pandas.core.frame.DataFrame): Dataframe to be plotted
        title: (str): Text to be used as title for the plot
    """
    fig, ax = plt.subplots(figsize=(10, 4))

    df.set_index('product_name').plot(kind='barh', ax=ax, legend=False)
    for i, v in enumerate(df['total']):
        ax.text(v, i, str(large_num_formatter(v)), color='blue', va='center',
                fontweight='bold')

    if title:
        ax.set_title(title)
    ax.set_ylabel('Produto')
    plt.xlabel('Valor total anual (US$)')

    ax.set_yticklabels([fill(p, 50) for p in df['product_name']])
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(large_num_formatter))

    plt.tight_layout()
    png_image = io.BytesIO()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(png_image)

    png_image_in_base_64 = 'data:image/png;base64,{}'.format(
        base64.b64encode(png_image.getvalue()).decode('utf8')
    )

    # Response(png_image.getvalue(), mimetype='image/png')
    return png_image_in_base_64


@app.route('/')
@app.route('/dashboard')
@app.route('/dashboard/')
@app.route('/dashboard/<string:state_code>/<int:year>')
@app.route('/dashboard/<string:state_code>/<int:year>/<int:month>')
def dashboard(state_code=None, year=None, month=None):
    """
    Show statistics about imports and exports for the state and year provided
    in the URL.

    Parameters:
        state_code: (str): The code of the state of origin/destiny the trade
        (default the first state available).
        year: (int): The year of the trade (default the first year available).
    """
    available_states = get_available_federative_units()
    if state_code is None:
        state_code = str(available_states.index[0])
    if state_code in available_states.index:
        state_name = available_states['name'][state_code]
        available_years = get_available_years()
        if year is None:
            year = available_years[0]
        if year in available_years:
            month_options = get_month_options(year)

            if month_options and month in month_options:
                month_name = get_month_name(month)
            else:
                month = None
                month_name = 'todos os meses'
            group = f'({state_name}, {month_name} de {year})'
            img_imports = get_plot(
                get_top('import', state_code, year, month),
                title=f'Produtos mais importados {group}'
            )
            img_exports = get_plot(
                get_top('export', state_code, year, month),
                title=f'Produtos mais exportados {group}'
            )
            return render_template(
                'dashboard.html',
                month_options=[None] + month_options,
                month=month,
                get_month_name=get_month_name,
                available_years=available_years,
                year=year,
                last_year=datetime.now().year - 1,
                available_states=available_states,
                state_code=state_code,
                img_imports=img_imports,
                img_exports=img_exports
            )
    return 'Parâmetro(s) inválido(s).'


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

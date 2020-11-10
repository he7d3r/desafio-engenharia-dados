from flask import Flask, render_template
from sqlalchemy import create_engine
from textwrap import fill
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg

app = Flask(__name__)

DATABASE_URI = 'sqlite:////data/trades.db'
engine = create_engine(DATABASE_URI)


def get_available_federative_units():
    """
    Get states codes from DB and return them as a list
    """
    with engine.connect() as connection:
        query = 'SELECT DISTINCT(SG_UF) FROM uf ORDER BY SG_UF'
        return pd.read_sql(query, connection).iloc[:, 0].values


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


def get_top(table, state, year, count=3):
    """
    Get products with the largest FOB values in USD and return them as a
    dataframe.

    Parameters:
        table: (str): The kind of trade. One of 'import' or 'export'.
        state: (str): The UF code of the state of origin/destiny the trade
        year: (str): The year of the trade
        count: (int): How many items to get
    """
    with engine.connect() as connection:
        query = f'''
        SELECT n.NO_NCM_POR product_name,
            t.total
        FROM top_by_state_and_year t
        JOIN uf u ON t.federative_unit=u.SG_UF
        JOIN ncm n ON t.product=n.CO_NCM
        WHERE t.year="{year}"
          AND t.federative_unit="{state}"
          AND t.kind="{table}"
        GROUP BY t.product
        ORDER BY t.total DESC
        LIMIT {count}
        '''
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

    df.set_index('product_name').plot(kind='barh', ax=ax)
    ax.legend(['Valor'])
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
    # plt.show()
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
@app.route('/dashboard/<string:state>/<int:year>')
def dashboard(state=None, year=None):
    """
    Show statistics about imports and exports for the state and year provided
    in the URL.

    Parameters:
        state: (str): The UF code of the state of origin/destiny the trade
        (default the first state available).
        year: (int): The year of the trade (default the first year available).
    """
    available_states = get_available_federative_units()
    if state is None:
        state = str(available_states[0])
    if state in available_states:
        available_years = get_available_years()
        if year is None:
            year = available_years[0]
        if year in available_years:
            df_imp = get_top('import', state, year)
            df_exp = get_top('export', state, year)
            img_imports = get_plot(df_imp, title='Produtos mais importados')
            img_exports = get_plot(df_exp, title='Produtos mais exportados')
            return render_template(
                'dashboard.html',
                state=state,
                year=year,
                years=available_years,
                states=available_states,
                imports=df_imp,
                exports=df_exp,
                img_imports=img_imports,
                img_exports=img_exports
            )
    return 'Parâmetro(s) inválido(s).'


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

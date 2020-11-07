from flask import Flask, render_template
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)

def get_available_states():
    """
    Get states codes from DB and return them as a list
    """
    eng = create_engine('sqlite:////data/trades.db')
    conn = eng.connect()
    query = 'SELECT DISTINCT(SG_UF) FROM uf ORDER BY SG_UF'
    return pd.read_sql(query, conn).iloc[:, 0].values

def get_available_years():
    """
    Get the years which are present in the DB and return them as a list of integers
    """
    eng = create_engine('sqlite:////data/trades.db')
    conn = eng.connect()
    query = 'SELECT DISTINCT(strftime("%Y", DATA)) year FROM export ORDER BY year'
    return pd.read_sql(query, conn).year.astype(int).values.tolist()

def get_top3(table, state, year):
    """
    Get products with the 3 largest FOB values in USD and return them as a dataframe

    Args:
        table: (str): The kind of trade. One of 'import' or 'export'.
        state: (str): The UF code of the state of origin/destiny the trade
        year: (str): The year of the trade
    """
    eng = create_engine('sqlite:////data/trades.db')
    conn = eng.connect()
    query = '''SELECT NO_NCM_POR item,
    SUM(VL_FOB) total
    FROM {table} k
    JOIN uf u ON SG_UF_NCM=u.SG_UF
    JOIN ncm n ON k.CO_NCM=n.CO_NCM
    WHERE strftime("%Y", DATA)="{year}"
      AND SG_UF_NCM="{state}"
    GROUP BY k.CO_NCM
    ORDER BY total DESC
    LIMIT 3
    '''.format(table=table, year=year, state=state)
    df = pd.read_sql(query, conn)
    return df

@app.route('/')
@app.route('/dashboard')
@app.route('/dashboard/')
@app.route('/dashboard/<string:state>/<int:year>')
def dashboard(state=None, year=None):
    """
    Show statistics about imports and exports for the state and year provided in the URL

    Args:
        state: (str): The UF code of the state of origin/destiny the trade (default the first state available)
        year: (int): The year of the trade (default the first year available)
    """
    available_states = get_available_states()
    if state is None:
        state = str(available_states[0])
    if state in available_states:
        available_years = get_available_years()
        if year is None:
            year = available_years[0]
        if year in available_years:
            df_imp = get_top3('import', state, year)
            df_exp = get_top3('export', state, year)
            return render_template(
                'dashboard.html',
                state=state,
                year=year,
                years=available_years,
                states=available_states,
                imports=df_imp,
                exports=df_exp
            )
    return f'Parâmetro(s) inválido(s).'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

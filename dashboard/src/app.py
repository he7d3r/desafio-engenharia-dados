from flask import Flask, render_template
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)

def get_available_states():
    eng = create_engine('sqlite:////data/trades.db')
    conn = eng.connect()
    query = 'SELECT DISTINCT(SG_UF) FROM uf ORDER BY SG_UF'
    return pd.read_sql(query, conn).iloc[:, 0].values

def get_available_years():
    eng = create_engine('sqlite:////data/trades.db')
    conn = eng.connect()
    query = 'SELECT DISTINCT(CO_ANO) FROM export ORDER BY CO_ANO'
    return pd.read_sql(query, conn).iloc[:, 0].values

def get_top3(table, state, year):
    eng = create_engine('sqlite:////data/trades.db')
    conn = eng.connect()
    query = '''SELECT NO_NCM_POR item,
    SUM(VL_FOB) total
    FROM {table}
    JOIN uf u ON SG_UF_NCM=u.SG_UF
    JOIN ncm n ON {table}.CO_NCM=n.CO_NCM
    WHERE CO_ANO={year}
      AND SG_UF_NCM="{state}"
    GROUP BY {table}.CO_NCM
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

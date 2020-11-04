from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello world!'

@app.route('/dashboard')
def dashboard():
    return """<table>
<caption>Simple table</caption>
<tbody>
<tr><th>A</th><th>B</th></tr>
<tr><td>1</td><td>2</td></tr>
<tr><td>3</td><td>4</td></tr>
</tbody>
</table>"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
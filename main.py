from flask import Flask, render_template, g, request
import requests
import sqlite3


app = Flask(__name__)


DATABASE = 'database.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        db = g._database = conn
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def hello_world():
    return render_template('template_Main_Page.html')


@app.route('/eur_to_<string:currency>/<int:amount>')
def get_converted_amount(currency, amount):
    return str(calculate_converted_amount(currency, amount))


@app.route('/history/currency/<string:currency>')
def get_history_by_currency(currency):
    currency = currency.upper()
    connection = get_db()
    cursor = connection.cursor()
    resp = cursor.execute("""
                    select id, currency_to, exchange_rate, amount, "result"
                    from exchange 
                    where currency_to = ?;
                """, (currency,))
    resp = resp.fetchall()
    lines = resp_parser(resp, cursor)
    return render_template('template_history.html', route_elements=lines)


@app.route('/history/amount_gte/<int:amount>')
def get_history_by_amount(amount):
    connection = get_db()
    cursor = connection.cursor()
    resp = cursor.execute("""
                    select id, currency_to, exchange_rate, amount, "result"
                    from exchange 
                    where amount >= ?;
                """, (amount,))
    resp = resp.fetchall()
    lines = resp_parser(resp, cursor)
    return render_template('template_history.html', route_elements=lines)


@app.route('/history/statistics/')
def get_history_statistics():
    connection = get_db()
    cursor = connection.cursor()
    resp = cursor.execute("""
                select currency_to, count(*), sum(result)
                from exchange 
                group by currency_to
            """, ())
    resp = resp.fetchall()
    lines = resp_parser(resp, cursor)
    return render_template('template_history.html', route_elements=lines)


@app.route('/history/')
def get_history():
    connection = get_db()
    cursor = connection.cursor()
    resp = cursor.execute("""
                select id, currency_to, exchange_rate, amount, "result"
                from exchange 
            """, ())
    resp = resp.fetchall()
    lines = resp_parser(resp, cursor)
    return render_template('template_history.html', route_elements=lines)


def resp_parser(resp, cursor):
    # data = []
    # for i in range(len(resp)):
    #     data.append(dict(zip([c[0] for c in cursor.description], resp[i])))
    # lines = []
    # for elem in data:
    #     output = ", ".join([str(elem[k]) for k in elem.keys()])
    #     lines.append(output)
    lines = [get_line(row) for row in resp]

    return lines


def get_line(row):
    return ', '.join([str(row[k]) for k in row.keys()])


def get_rate(currency):
    response = requests.get('https://api.exchangeratesapi.io/latest')
    response_json = response.json()
    rates = response_json['rates']
    return rates[currency]


def calculate_converted_amount(currency, amount):
    currency = currency.upper()
    rate = get_rate(currency)
    converted_amount = rate * amount
    write_to_db(currency, rate, amount, converted_amount)
    return converted_amount


def write_to_db(*args):
    conn = get_db()
    cursor = conn.cursor()
    resp = cursor.execute("""
        insert into exchange(currency_to, exchange_rate, amount, 'result')
            values(?, ?, ?, ?)
    """, args)
    conn.commit()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


if __name__ == '__main__':
    # init_db()
    app.run()

from flask import Flask, render_template
import requests


app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('template_Main_Page.html')


@app.route('/eur_to_usd/<int:amount>')
def get_USD(amount):
    rate = get_rate("USD")
    write_to_file("USD", rate)
    converted_amount = rate*amount
    write_to_file("USD", rate, amount, converted_amount)
    return str(converted_amount)


@app.route('/eur_to_gbp/<int:amount>')
def get_GBP(amount):
    rate = get_rate("GBP")
    converted_amount = rate * amount
    write_to_file("USD", rate, amount, converted_amount)
    return str(converted_amount)


@app.route('/eur_to_php/<int:amount>')
def get_PHP(amount):
    rate = get_rate("PHP")
    converted_amount = rate * amount
    write_to_file("USD", rate, amount, converted_amount)
    return str(converted_amount)


def get_rate(currency):
    response = requests.get('https://api.exchangeratesapi.io/latest')
    response_json = response.json()
    rates = response_json['rates']
    return rates[currency]


def write_to_file(*args):
    f = open("history.txt", "a")
    list_elements = [str(x) for x in [*args]]
    f.write(', '.join(list_elements))
    f.write('\n')
    f.close()


if __name__ == '__main__':
    app.run()
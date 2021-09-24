from flask import Flask, request, render_template
from urllib.parse import urlparse
app = Flask(__name__)
database = dict()


@app.route('/counter', methods=['GET', 'POST'])
def counter_page():
    origin = request.headers.get('Referer')
    if origin not in database:
        database[origin] = 1
    else:
        database[origin] += 1
    return render_template("counter.html", visitors_count=database[origin])


@app.route('/test', methods=['GET', 'POST'])
def test_page():
    return render_template("test.html")


@app.route('/')
def main_page():
    return render_template("main.html", url=f'http{"s" if request.is_secure else ""}://{request.host}/counter')

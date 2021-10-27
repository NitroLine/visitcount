from flask import render_template, url_for, request

from .app import app


@app.route('/test', methods=['GET', 'POST'])
def test_page():
    return render_template("test.html")


@app.route('/test2', methods=['GET', 'POST'])
def test_2_page():
    return render_template("test.html")


@app.route('/')
def main_page():
    js_url = f'http{"s" if request.is_secure else ""}:/' \
             f'/{request.host}{url_for("static", filename="js/counter.js")}'
    return render_template("main.html", url=js_url)


@app.route('/graphics')
def statistics_page():
    return render_template("graphic_stats.html")

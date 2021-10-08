import datetime as dt

from flask import Flask, request, render_template, url_for, jsonify
from flask_cors import CORS, cross_origin

from .config import DATABASE_PARAMS
from .storage import RedisStorage, VisitInfo

app = Flask(__name__)
database = RedisStorage(DATABASE_PARAMS)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/test', methods=['GET', 'POST'])
def test_page():
    return render_template("test.html")


@app.route('/test2', methods=['GET', 'POST'])
def test_2_page():
    return render_template("test.html")


@app.route('/')
def main_page():
    js_url = f'http{"s" if request.is_secure else ""}://{request.host}{url_for("static", filename="js/counter.js")}'
    return render_template("main.html", url=js_url)


@app.route('/origins/')
def get_all_origins():
    return jsonify(database.get_all_origins())


@app.route('/graphics')
def statistics_page():
    return render_template("graphic_stats.html")


@app.route('/stats/<origin>/', methods=['POST'])
def statistics_at_interval(origin):
    json = request.json
    start_date = dt.datetime.strptime(json['start_date'], '%Y-%m-%d')
    end_date = dt.datetime.strptime(json['start_date'], '%Y-%m-%d')
    result_data = []
    while start_date <= end_date:
        result_data.append(database.get_origin_statistics_at_date(origin, str(start_date.date())))
        start_date += dt.timedelta(days=1)
    return jsonify(result_data)


@app.route('/stats/<origin>/<date>')
def statistics_at_date(origin, date):
    stats = database.get_origin_statistics_at_date(origin, date)
    return jsonify(stats)


@app.route('/api/counter', methods=['POST'])
@cross_origin()
def counter():
    json = request.json
    info = VisitInfo(json['origin'], json['client_id'], json['path'], json['referer'], request.user_agent.browser,
                     request.accept_languages.best, request.user_agent.platform)
    database.add_information(info)
    return jsonify(success=True)

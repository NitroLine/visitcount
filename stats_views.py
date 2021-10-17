import datetime as dt

from flask import request, jsonify

from .app import app, database


@app.route('/origins/')
def get_all_origins():
    return jsonify(database.get_all_origins())


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

from flask import Flask, request, render_template, url_for, jsonify
from .storage import RedisStorage, DictStorage, VisitInfo
from flask_cors import CORS, cross_origin
from .config import DATABASE_PARAMS
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


@app.route('/stats/<origin>')
def statistics_page(origin):
    stats = database.get_origin_statistics(origin)
    print(stats)
    return jsonify(stats)


@app.route('/api/counter', methods=['POST'])
@cross_origin()
def counter():
    json = request.json
    info = VisitInfo(json['origin'], json['client_id'], json['path'], json['referer'], request.user_agent.browser,
                     request.accept_languages.best, request.user_agent.platform)
    database.add_information(info)
    return jsonify(success=True)

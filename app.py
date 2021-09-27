from flask import Flask, request, render_template, url_for, jsonify
from urllib.parse import urlparse
from .storage import RedisStorage, DictStorage
from flask_cors import CORS, cross_origin
app = Flask(__name__)
database = DictStorage({'host':'localhost', 'db':0})
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/counter', methods=['GET', 'POST'])
def counter_page():
    origin = request.headers.get('Referer')
    error = None
    current = 0
    if origin is not None:
        try:
            current = database.increment_total_visits(origin)
        except Exception as err:
            error = f"Database error {str(err)}"
    else:
        error = "No Referer header in request for count"
    return render_template("counter.html", visitors_count=current, error=error)


@app.route('/test', methods=['GET', 'POST'])
def test_page():
    return render_template("test.html")


@app.route('/')
def main_page():
    js_url = f'http{"s" if request.is_secure else ""}://{request.host}{url_for("static", filename="js/counter.js")}'
    return render_template("main.html", url=js_url)


@app.route('/api/counter', methods=['POST'])
@cross_origin()
def counter():
    json = request.json
    print(json)
    print(request.remote_addr)
    print(request.url)
    return jsonify(success=True)
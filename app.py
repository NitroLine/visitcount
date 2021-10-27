from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from .config import DATABASE_PARAMS
from .storage import RedisStorage, VisitInfo

app = Flask(__name__)
database = RedisStorage(DATABASE_PARAMS)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/api/counter', methods=['POST'])
@cross_origin()
def counter():
    json = request.json
    info = VisitInfo(json['origin'], json['client_id'], json['path'],
                     json['referer'], request.user_agent.browser,
                     request.accept_languages.best,
                     request.user_agent.platform)
    database.add_information(info)
    return jsonify(success=True)

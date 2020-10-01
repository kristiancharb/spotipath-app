import db
from flask import Flask, request, jsonify, g
from flask_cors import CORS, cross_origin
import search

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
@cross_origin()
def test():
    return 'Welcome to the Spotipath API'

@app.route('/path/', methods=['GET'])
@cross_origin()
def path():
    src = request.args.get('src')
    dest = request.args.get('dest')
    if not src or not dest:
        return jsonify({
            'error': 'Request must include src (string) and dest(string)'
        }), 400

    try:
        path = search.get_path(src, dest)
    except db.InvalidArgument as error:
        return jsonify({
            'error': error.message
        }), 400
    except search.NoPathFound:
        return jsonify({
            'error': 'No path found between artists'
        }), 404

    return jsonify(path)

@app.route('/artists/', methods=['GET'])
@cross_origin()
def artists():
    query = request.args.get('q')
    if not query:
        return jsonify({
            'error': 'Request must include q (string)'
        }), 400

    artists = db.query_artist(query)
    return jsonify(artists)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()
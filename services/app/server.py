import db
from flask import Flask, request, jsonify, g
from flask_cors import CORS, cross_origin
import spotify
import search

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
@cross_origin()
def index():
    return 'Welcome to the Spotipath API'

@app.route('/test/')
@cross_origin()
def test():
    return 'This is a test route'

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

@app.route('/access-token/', methods=['GET'])
@cross_origin()
def access_token():
    try:
        token = spotify.get_spotify_token()
        return jsonify({
            'token': token
        })
    except:
        return jsonify({
            'error': 'Failed to fetch Spotify access token'
        })

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

if __name__ == '__main__':
    app.run(host= '0.0.0.0')
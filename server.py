import db
from flask import Flask, request, jsonify
import search

app = Flask(__name__)

@app.route('/')
def test():
    return 'Welcome to the Spotipath API'

@app.route('/path/', methods=['POST'])
def path():
    src = request.json.get('src')
    dest = request.json.get('dest')
    if not src or not dest:
        return jsonify({
            'error': 'Request must include src (string) and dest(string)'
        }), 400

    try:
        path = search.get_path(src, dest)
    except db.InvalidArgument:
        return jsonify({
            'error': 'Invalid artist name'
        }), 400
    except search.NoPathFound:
        return jsonify({
            'error': 'No path found between artists'
        }), 404

    return jsonify(path)
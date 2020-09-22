from flask import Flask, request, jsonify
import search

app = Flask(__name__)

@app.route('/')
def test():
    return 'Welcome to the Spotipath API'

@app.route('/path/', methods=['POST'])
def path():
    src = request.json['src']
    dest = request.json['dest']
    path = search.get_path(src, dest)
    return jsonify(path)
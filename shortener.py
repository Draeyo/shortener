#!/usr/bin/python
# encoding: utf-8

import os, tempfile, datetime
from pymongo import MongoClient
from flask import Flask, request, jsonify, url_for
from conf import MONGO_HOST, MONGO_USER, MONGO_PWD, MONGO_AUTH_SOURCE, HOST, PORT, DEBUG, APP_HOST

app = Flask(__name__)
client = MongoClient(MONGO_HOST, username=MONGO_USER, password=MONGO_PWD, authSource=MONGO_AUTH_SOURCE, authMechanism="SCRAM-SHA-1")
db = client['sharex']
collection = db['urls']

def get_name(prefix):
    tmp = tempfile.NamedTemporaryFile(prefix=prefix)
    name = str(tmp.name).rsplit('/', 1)[1]
    tmp.close()
    return str(name)

@app.route('/', methods=['GET'])
def home():
    return "URL Shortener", 200

@app.route('/short', methods=['POST'])
def short():
    if 'origin' in request.form and 'Content-Type' in request.headers and 'multipart/form-data' in request.headers['Content-Type']:
        entry = {}
        name = get_name('sh')
        entry['origin'] = request.form['origin']
        entry['short'] = name
        entry['date'] = datetime.datetime.utcnow()
        collection.insert_one(entry)
        return jsonify(status='ok', url=APP_HOST + url_for('to', code=name)), 200
    return jsonify(status='ko'), 400

@app.route('/to/<string:code>', methods=['GET'])
def to(code):
    entry = collection.find_one({'short': code})
    if 'origin' in entry:
        return jsonify(status='ok'), 302, {'Location': entry['origin']}
    return jsonify(status='ko'), 400

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)

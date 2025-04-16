import pymongo
from pymongo import MongoClient
from flask import Flask, request, render_template, jsonify, url_for, redirect
from app import app
from bson.json_util import dumps, loads
from markupsafe import escape

# from utils import *
import ast
import httplib2
import json


@app.route("/")
@app.route("/index")
def home():
    # current status?
    docs = []
    client = MongoClient("localhost", 27017)
    db = client["BatchRunStatus"]
    collection_batches = db["DetailStatus"]
    cursor = collection_batches.find({}, {"_id": False})
    # status = [document['BatchRunStatus'] for document in cursor]
    # print(cursor)
    for document in cursor:
        docs.append(document)
        # print(document)

    results = {"results": docs}
    print(results)

    return jsonify(results)  # "Wiki Refresh Api test slave databases"
    # return render_template('home.html')


@app.route("/status")
def status():
    # current status?
    docs = []
    client = MongoClient("localhost", 27017)
    try:
        db = client["BatchRunStatus"]
        collection_batches = db["OverallStatus"]
        cursor = collection_batches.find({}, {"_id": False})
        status = [document["OverallStatus"] for document in cursor]
        # print(cursor)
        # for document in cursor:
        # docs.append(document)
        # print(document)
        results = {"status": status[-1]}
    except Exception as e:
        print(e)
        results = {"status": None}

    # print(results)

    return jsonify(results)  # "Wiki Refresh Api test slave databases"
    # return render_template('home.html')


@app.route('/check_name/<name>')
def check_name(name):
    # Sanitize the input to prevent XSS
    pep_name = escape(name)

    resp, content = httplib2.Http().request("http://44.229.34.80:5001/check_name/%s" % pep_name)

    content = content.decode("utf-8")

    content = content.strip()

    content = json.loads(content)

    return jsonify(content)  # Return as JSON to ensure safe rendering


@app.route('/check2', methods=['GET', 'POST'])
def check2():
    if request.method == 'POST':
        user = request.form['pep_name']
        return redirect(url_for('check_name', name=escape(user)))
    else:
        user = request.args.get('pep_name')
        return redirect(url_for('check_name', name=escape(user)))
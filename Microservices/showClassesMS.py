import pymysql.cursors
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import requests
import os
import hashlib
import jwt
import json

# instantiate flask app
app = Flask(__name__)

# enables cross-origin resource sharing for fetch apis
CORS(app)

@app.route('/showUnassignedClasses', methods=['GET'])
def showUnassignedClasses():
    token = request.args.get('token')
    payload = {'token': token}
    url = "http://10.124.9.182:5003/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['status']):
        tutorID = validation['token']['tutorID']
        payload = {'tutorID': tutorID}
        url = "http://10.124.9.182:5003/getTutorInfo"
        response = requests.get(url, params=payload)
        result = response.json()
        eduLevel = result['eduLevel']
        taughtSubjects = result['taughtSubjects']
        payload = {'eduLevel': eduLevel, 'taughtSubjects': taughtSubjects}
        url = "http://10.124.9.182:5004/getUnassignedClasses"
        response = requests.get(url, params=payload)
        data = response.json()
        return jsonify(data)

@app.route('/showTutorClasses', methods=['GET'])
def showTutorClasses():
    token = request.args.get('token')
    payload = {'token': token}
    url = "http://10.124.9.182:5003/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['status']):
        tutorID = validation['token']['tutorID']
        payload = {'tutorID': tutorID}
        url = "http://10.124.9.182:5004/getTutorSchedule"
        response = requests.get(url, params=payload)
        data = response.json()
        return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)
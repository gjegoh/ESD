
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

@app.route('/registerClass', methods=['PATCH'])
def registerClass():
    data = request.get_json()
    token = data['token']
    payload = {'token': token}
    url = "http://10.124.9.182:5003/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['status']):
        scheduleID = data['scheduleID']
        tutorID = validation['token']['tutorID']
        url = "http://10.124.9.182:5004/updateClassTutor"
        payload = {'scheduleID': scheduleID, "tutorID": tutorID}
        response = requests.patch(url, params=payload)
        result = response.json()
        return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)
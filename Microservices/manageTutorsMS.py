from dataclasses import dataclass
import pymysql.cursors
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import hashlib
import jwt
import requests

# instantiate flask app
app = Flask(__name__)

# enables cross-origin resource sharing for fetch apis
CORS(app)


@app.route('/approveTutor', methods=['PATCH'])
def approveTutor():
    data = request.get_json()
    token = data['token']
    payload = {'token': token}
    url = "http://admin:5000/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['code'] < 300 and validation['token']['isAdmin']):
        email = data['email']
        payload = {'email': email, "action": "approve"}
        url = "http://tutor:5003/manageTutor"
        response = requests.patch(url, params=payload)
        status = response.json()
        #call notiMS and send tutor email
        approveTutorURL = "http://notification:5010/approveTutorNotification"
        response = requests.post(approveTutorURL, json=payload)
        if (status['code'] < 300):   
            return jsonify(data)

@app.route('/rejectTutor', methods=['DELETE'])
def rejectTutor():     
    data = request.get_json()
    token = data['token']
    payload = {'token': token}
    url = "http://admin:5000/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['code'] < 300 and validation['token']['isAdmin']):
        email = data['email']
        payload = {'email': email, "action": "delete"}
        url = "http://tutor:5003/manageTutor"
        response = requests.delete(url, params=payload)
        status = response.json()
        #call notiMS and send tutor email
        rejectTutorURL = "http://notification:5010/rejectTutorNotification"
        response = requests.post(rejectTutorURL, json=payload)
        if (status['code'] < 300):
            return jsonify(
                {
                    "code": 200,
                    'message': 'Tutor is rejected successfully.'
                }
            )
            

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
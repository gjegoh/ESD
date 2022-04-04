
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

@app.route('/scheduleCreation', methods=['POST'])
def scheduleCreation():
    data = request.get_json()
    token = data['token']
    payload = {'token': token}
    # url = "http://10.124.9.182:5000/validateToken"
    # url = "http://10.124.141.82:5000/validateToken"
    url = "http://admin:5000/validateToken"


    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['code'] < 300 and validation['token']['isAdmin']): 
        payload = data
        # url = "http://10.124.9.182:5004/createClassSchedule"
        # url = "http://192.168.1.8:5004/createClassSchedule"
        url = "http://classSchedule:5004/createClassSchedule"

        response = requests.post(url, data=payload)
        data = response.json()
        # include notiMS
        # data['code'] = 200
        return jsonify(data)
    else:
        return jsonify(
            {
            'code': validation['code'],
            'error': 'Invalid authorisation. Please re-login.'
            }
        )
    
# add delete class schedules

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
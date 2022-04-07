
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
        return jsonify({
            'code': 200,
            'message': 'Successful creation of class schedules.'

        })
    else:
        return jsonify(
            {
            'code': 401,
            'message': 'Invalid authorisation. Please re-login.'
            }
        )
    
# add delete class schedules

@app.route('/getStudents', methods=['GET'])
def getStudents():
    scheduleID = request.args.get('scheduleID')
    url = "http://classSchedule:5004/getStudentList"
    payload = {'scheduleID': scheduleID}
    response = requests.get(url, params=payload)
    result = response.json()
    studentList = result['studentList']
    if (len(studentList) >= 1):
        url = "http://student:5005/getStudentNames"
        payload = {'studentList': studentList}
        response = requests.get(url, params=payload)
        result = response.json()
        return jsonify(
            {
                'code': 200,
                'students': result['data']
            }
        )
    else:
        return jsonify(
            {
                'students': [] 
            }
        )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
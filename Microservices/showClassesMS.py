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
    # url = "http://10.124.9.182:5003/validateToken"
    url = "http://tutor:5003/validateToken"

    # url = "http://tutor:5003/validateToken?token={token}".format(token=token)

    response = requests.get(url, params=payload)
    # response = requests.request('GET',url,json=None)
    validation = response.json()
    if (validation['status']):
        tutorID = validation['token']['tutorID']
        payload = {'tutorID': tutorID}
        # url = "http://10.124.9.182:5003/getTutorInfo"
        url = "http://tutor:5003/getTutorInfo"

        response = requests.get(url, params=payload)
        result = response.json()
        eduLevel = result['eduLevel']
        taughtSubjects = result['taughtSubjects']
        payload = {'eduLevel': eduLevel, 'taughtSubjects': taughtSubjects}
        # url = "http://10.124.9.182:5004/getUnassignedClasses"
        url = "http://classSchedule:5004/getUnassignedClasses"

        response = requests.get(url, params=payload)
        data = response.json()
        return jsonify(data)

@app.route('/showTutorClasses', methods=['GET'])
def showTutorClasses():
    token = request.args.get('token')
    payload = {'token': token}
    # url = "http://10.124.9.182:5003/validateToken"
    url = "http://tutor:5003/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['status']):
        tutorID = validation['token']['tutorID']
        payload = {'tutorID': tutorID}
        # url = "http://10.124.9.182:5004/getTutorSchedule"
        url = "http://classSchedule:5004/getTutorSchedule"

        response = requests.get(url, params=payload)
        data = response.json()
        return jsonify(data)
    
@app.route('/showAvailableClasses', methods=['GET'])
def showAvailableClasses():
    newScheduleList = []
    token = request.args.get('token')
    payload = {'token': token}
    # url = "http://10.124.9.182:5005/validateToken"
    url = "http://student:5005/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['status']):
        grade = validation['token']['grade']
        studentID = validation['token']['studentID']
        payload = {'grade': grade}
        # url = "http://10.124.9.182:5004/getClassTutors"
        url = "http://classSchedule:5004/getClassTutors"
        response = requests.get(url, params=payload)
        data = response.json()
        classDict = data['classDict']
        tutorList = data['tutorList']
        scheduleList = data['scheduleList']
        payload = {'tutorList': tutorList}
        # url = "http://10.124.9.182:5003/getTutorName"
        url = "http://tutor:5003/getTutorName"
        response = requests.get(url, params=payload)
        data = response.json()
        tutorDict = {i['tutorID']: i['firstName'] + " " + i['lastName'] for i in data}
        payload = {'studentID': studentID}
        url = "http://student:5005/getClassesBooked"
        response = requests.get(url, params=payload)
        data = response.json()
        bookedSchedules = data['bookedSchedules']
        for schedule in scheduleList:
            if (schedule['scheduleID'] not in bookedSchedules):
                schedule['tutorName'] = tutorDict[schedule['tutorID']]
                newScheduleList.append(schedule)
        return jsonify(
            {
                "scheduleList": newScheduleList,
                "classDict": classDict,
                'studentID': studentID
            }
        )
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)
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
    url = "http://tutor:5003/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
    # code < 300 = success validation
    if (validation['code'] < 300):
        tutorID = validation['token']['tutorID']
        payload = {'tutorID': tutorID}
        url = "http://tutor:5003/getTutorInfo"
        response = requests.get(url, params=payload)
        result = response.json()
        eduLevel = result['eduLevel']
        taughtSubjects = result['taughtSubjects']
        payload = {'eduLevel': eduLevel, 'taughtSubjects': taughtSubjects}
        url = "http://classSchedule:5004/getUnassignedClasses"
        response = requests.get(url, params=payload)
        data = response.json()
        data['code'] = 201
        return jsonify(data)
    else:
        # validation fails, possible expiring of token
        return jsonify(
            {
                "code": 403,
                "message": "Token expired."
            }
        )

@app.route('/showTutorClasses', methods=['GET'])
def showTutorClasses():
    token = request.args.get('token')
    payload = {'token': token}
    # url = "http://10.124.9.182:5003/validateToken"
    url = "http://tutor:5003/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
    
    # code < 300 = success validation
    if (validation['code'] < 300):
        tutorID = validation['token']['tutorID']
        payload = {'tutorID': tutorID}
        # url = "http://10.124.9.182:5004/getTutorSchedule"
        url = "http://classSchedule:5004/getTutorSchedule"

        response = requests.get(url, params=payload)
        data = response.json()
        data['code'] = 201
        return jsonify(data)
    else:
        # code > 400 = error
        # validation fails, possibly the expiring of credential token
        return jsonify({
        "code": 403,
        "message": "Token expired."
    })
        
    
@app.route('/showAvailableClasses', methods=['GET'])
def showAvailableClasses():
    newScheduleList = []
    token = request.args.get('token')
    payload = {'token': token}
    # url = "http://10.124.9.182:5005/validateToken"
    url = "http://student:5005/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['code']<300):
        grade = validation['token']['grade']
        studentID = validation['token']['studentID']
        payload = {'grade': grade}
        url = "http://classSchedule:5004/getClassTutors"
        response = requests.get(url, params=payload)
        data = response.json()
        classDict = data['classDict']
        tutorList = data['tutorList']
        scheduleList = data['scheduleList']
        payload = {'tutorList': tutorList}
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
                "code": 201,
                "scheduleList": newScheduleList,
                "classDict": classDict,
                'studentID': studentID
            }
        )
    # invalid token
    else:
        return jsonify(
            {
                "code": 403,
                "message": "Token expired."
            }
        )

@app.route('/showStudentClasses', methods=['GET'])
def showStudentClasses():
    token = request.args.get('token')
    payload = {'token': token}
    url = "http://student:5005/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['code']<300):
        studentID = validation['token']['studentID']
        payload = {'studentID': studentID}
        url = "http://student:5005/getClassesBooked"
        response = requests.get(url, params=payload)
        data = response.json()
        # no schedule for 
        if (len(data['bookedSchedules']) == 0):
            return jsonify(
                {
                    "code": 202,
                    "message": "There are no schedule for viewing. Please enrol into new class."
                })
        # Produces http 500, database error, return as it is
        elif (data['code']>300):
            return jsonify(
                {
                    "code": 500,
                    "message": "Database erorr, please contact administrator"
                })
        
        bookedSchedules = data['bookedSchedules']
        payload = {'bookedSchedules': bookedSchedules}
        url = "http://classSchedule:5004/getStudentSchedule"
        response = requests.get(url, params=payload)
        data = response.json()
        # 
        if (data['code']>300):
            return data
        
        scheduleList = data['scheduleList']
        classDict = data['classDict']
        tutorList = list(set([i['tutorID'] for i in scheduleList]))
        payload = {'tutorList': tutorList}
        url = "http://tutor:5003/getTutorName"
        response = requests.get(url, params=payload)
        data = response.json()
        tutorDict = {i['tutorID']: i['firstName'] + " " + i['lastName'] for i in data}
        newScheduleList = []
        try:
            for schedule in scheduleList:
                schedule['tutorName'] = tutorDict[schedule['tutorID']]
                newScheduleList.append(schedule)
        except KeyError:
            pass
        return jsonify(
            {
                "code": 201,
                "scheduleList": newScheduleList,
                "classDict": classDict
            }
        )
    # invalid token
    # inside should be code:403 and error message
    return jsonify(
            {
                "code": 403,
                "message": "Token expired."
            }
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)
import pymysql.cursors
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import requests
import os
import hashlib
import jwt

# instantiate flask app
app = Flask(__name__)

# enables cross-origin resource sharing for fetch apis
CORS(app)


@app.route('/getClassDetails', methods=['GET'])
def getClassDetails():
    token = request.args.get('token')
    payload = {'token': token}
    # url = "http://10.124.9.182:5000/validateToken"
    url = "http://192.168.1.8:5000/validateToken"

    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['status']):
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                    user='admin',
                                    password='thisismypw',
                                    cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                sql = "USE classScheduleDB"
                cursor.execute(sql)
                connection.commit()
                sql = "SELECT DISTINCT subject FROM Class"
                cursor.execute(sql)
                result = cursor.fetchall()
                subjectList = [i['subject'] for i in result]
                sql = "SELECT DISTINCT grade FROM Class"
                cursor.execute(sql)
                result = cursor.fetchall()
                gradeList = [i['grade'] for i in result]
                return jsonify(
                    {
                        "data": {
                            "subject": subjectList,
                            "grade": gradeList
                        }
                    }
                )


@app.route('/createClassSchedule', methods=['POST'])
def createClassSchedule():
    data = request.form.to_dict(flat=False)
    print(data)
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            chosenSubjects = data['subjects']
            chosenGrades = data['grades']
            chosenYears = data['years']
            chosenDays = data['days']
            chosenTimings = data['timings']
            sql = "USE classScheduleDB"
            cursor.execute(sql)
            connection.commit()
            classIDList = []
            for subject in chosenSubjects:
                for grade in chosenGrades:
                    sql = "SELECT classID FROM Class WHERE subject='{subject}' and grade='{grade}'".format(
                        subject=subject, grade=grade)
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    print(result)
                    classIDList.append(result[0]['classID'])
            for classID in classIDList:
                for year in chosenYears:
                    for day in chosenDays:
                        for timing in chosenTimings:
                            sql = "INSERT INTO classSchedule (classID, year, day, timing) VALUES ({classID}, {year}, '{day}', {timing})".format(
                                classID=classID, year=year, day=day, timing=timing)
                            cursor.execute(sql)
                            connection.commit()
            return jsonify(data)


@app.route('/getClassSchedules', methods=['GET'])
def getClassSchedules():
    token = request.args.get('token')
    payload = {'token': token}
    # url = "http://10.124.9.182:5000/validateToken"
    url = "http://192.168.1.8:5000/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['status']):
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                    user='admin',
                                    password='thisismypw',
                                    cursorclass=pymysql.cursors.DictCursor)
        scheduleList = []
        classDict = {}
        with connection:
            with connection.cursor() as cursor:
                sql = "USE classScheduleDB"
                cursor.execute(sql)
                connection.commit()
                sql = "SELECT * FROM classSchedule"
                cursor.execute(sql)
                scheduleList = cursor.fetchall()
                sql = "SELECT classID, subject, grade FROM Class"
                cursor.execute(sql)
                result = cursor.fetchall()
                for details in result:
                    classDict[details['classID']] = [
                        details['subject'], details['grade']]
                return jsonify(
                    {
                        "data": {
                            "scheduleList": scheduleList,
                            "classDict": classDict
                        }
                    }
                )


@app.route('/getUnassignedClasses', methods=['GET'])
def getUnassignedClasses():
    token = request.args.get('token')
    payload = {'token': token}
    # url = "http://192.168.86.129:5003/validateToken"
    url = "http://192.168.1.8:5000/validateToken"

    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['status']):
        tutorID = validation['token']['tutorID']
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                    user='admin',
                                    password='thisismypw',
                                    cursorclass=pymysql.cursors.DictCursor)
        scheduleList = []
        classDict = {}
        with connection:
            with connection.cursor() as cursor:
                payload = {'tutorID': tutorID}
                url = "http://192.168.86.129:5003/getTutorInfo"
                response = requests.get(url, params=payload)
                result = response.json()
                eduLevel = result['eduLevel']
                taughtSubjects = tuple(result['taughtSubjects'].split(','))
                sql = "USE classScheduleDB"
                cursor.execute(sql)
                connection.commit()
                sql = "SELECT classID, subject, grade FROM Class WHERE grade LIKE '{eduLevel}%' AND subject IN {taughtSubjects}".format(
                    eduLevel=eduLevel, taughtSubjects=taughtSubjects)
                cursor.execute(sql)
                result = cursor.fetchall()
                classIDList = tuple([i['classID'] for i in result])
                classDict = {i['classID']: [i['subject'], i['grade']]
                            for i in result}
                sql = "SELECT * FROM classSchedule WHERE classID IN {classIDList} AND tutorID IS NULL".format(
                    classIDList=classIDList)
                cursor.execute(sql)
                scheduleList = cursor.fetchall()
                return jsonify(
                    {
                        "scheduleList": scheduleList,
                        "classDict": classDict
                    }
                )


@app.route('/registerClass', methods=['PATCH'])
def registerClass():
    data = request.get_json()
    token = data['token']
    payload = {'token': token}
    # url = "http://192.168.86.129:5003/validateToken"
    url = "http://192.168.1.8:5000/validateToken"

    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['status']):
        scheduleID = data['scheduleID']
        tutorID = validation['token']['tutorID']
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                    user='admin',
                                    password='thisismypw',
                                    cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                sql = "USE classScheduleDB"
                cursor.execute(sql)
                connection.commit()
                sql = "UPDATE classSchedule SET tutorID={tutorID} WHERE scheduleID={scheduleID}".format(
                    tutorID=tutorID, scheduleID=scheduleID)
                cursor.execute(sql)
                connection.commit()
                return data


@app.route('/getMySchedule', methods=['GET'])
def getMySchedule():
    token = request.args.get('token')
    payload = {'token': token}
    # url = "http://192.168.86.129:5003/validateToken"
    url = "http://192.168.1.8:5000/validateToken"

    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['status']):
        tutorID = validation['token']['tutorID']
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                    user='admin',
                                    password='thisismypw',
                                    cursorclass=pymysql.cursors.DictCursor)
        scheduleList = []
        classDict = {}
        with connection:
            with connection.cursor() as cursor:
                sql = "USE classScheduleDB"
                cursor.execute(sql)
                connection.commit()
                sql = "SELECT * FROM classSchedule WHERE tutorID={tutorID}".format(
                    tutorID=tutorID)
                cursor.execute(sql)
                scheduleList = cursor.fetchall()
                sql = "SELECT classID, subject, grade FROM Class"
                cursor.execute(sql)
                result = cursor.fetchall()
                classDict = {i['classID']: [i['subject'], i['grade']]
                            for i in result}
                return jsonify(
                    {
                        "scheduleList": scheduleList,
                        "classDict": classDict
                    }
                )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)

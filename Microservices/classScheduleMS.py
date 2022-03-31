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

@app.route('/getUnassignedClasses', methods=['GET'])
def getUnassignedClasses():
    eduLevel = request.args.get('eduLevel')
    taughtSubjects = tuple(request.args.get('taughtSubjects').split(','))
    scheduleList = []
    classDict = {}
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                    user='admin',
                                    password='thisismypw',
                                    cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
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

@app.route('/getClassSchedules', methods=['GET'])
def getClassSchedules():
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

@app.route('/updateClassTutor', methods=['PATCH'])
def updateClassTutor():
    data = request.args
    scheduleID = data['scheduleID']
    tutorID = data['tutorID']
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
            return jsonify(data)


@app.route('/getTutorSchedule', methods=['GET'])
def getTutorSchedule():
    tutorID = request.args.get('tutorID')
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
                
@app.route('/getStudentSchedule', methods=['GET'])
def getStudentSchedule():
    token = request.args.get('token')
    payload = {'token': token}
    url = "http://10.124.9.182:5005/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
    if (validation['status']):
        grade = validation['token']['grade']
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                    user='admin',
                                    password='thisismypw',
                                    cursorclass=pymysql.cursors.DictCursor)
        scheduleList = []
        newScheduleList = []
        classDict = {}
        relevantSchedules = []
        with connection:
            with connection.cursor() as cursor:
                sql = "USE classScheduleDB"
                cursor.execute(sql)
                connection.commit()
                sql = "SELECT classID, subject, grade FROM Class"
                cursor.execute(sql)
                result = cursor.fetchall()
                classDict = {i['classID']: [i['subject'], i['grade']]
                            for i in result}
                relevantSchedules = tuple([i['classID'] for i in result if i['grade']==grade])
                sql = "SELECT * from classSchedule WHERE classID IN {relevantSchedules} AND tutorID IS NOT NULL".format(relevantSchedules=relevantSchedules)
                cursor.execute(sql)
                scheduleList = cursor.fetchall()
                tutorList = list(set([i['tutorID'] for i in scheduleList]))
                payload = {'tutorList': tutorList}
                url = "http://10.124.9.182:5003/getTutorName"
                response = requests.get(url, params=payload)
                data = response.json()
                tutorDict = {i['tutorID']: i['firstName'] + " " + i['lastName'] for i in data}
                for schedule in scheduleList:
                    schedule['tutorName'] = tutorDict[schedule['tutorID']]
                    newScheduleList.append(schedule)
                return jsonify(
                    {
                        "scheduleList": newScheduleList,
                        "classDict": classDict
                    }
                )



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)

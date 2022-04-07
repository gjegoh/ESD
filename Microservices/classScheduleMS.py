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
            data['code'] = 200
            return jsonify(data)

@app.route('/getUnassignedClasses', methods=['GET'])
def getUnassignedClasses():
    eduLevel = request.args.get('eduLevel')
    data = request.args.get('taughtSubjects').split(',')
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
            if (len(data) > 1):
                taughtSubjects = tuple(data)
                sql = "SELECT classID, subject, grade FROM Class WHERE grade LIKE '{eduLevel}%' AND subject IN {taughtSubjects}".format(
                eduLevel=eduLevel, taughtSubjects=taughtSubjects)
            else:
                taughtSubjects = data[0]
                sql = "SELECT classID, subject, grade FROM Class WHERE grade LIKE '{eduLevel}%' AND subject='{taughtSubjects}'".format(
                eduLevel=eduLevel, taughtSubjects=taughtSubjects)
            cursor.execute(sql)
            result = cursor.fetchall()
            classDict = {i['classID']: [i['subject'], i['grade']]
                        for i in result}
            if (len(result) > 1):
                classIDList = tuple([i['classID'] for i in result])
                sql = "SELECT * FROM classSchedule WHERE classID IN {classIDList} AND tutorID IS NULL".format(
                classIDList=classIDList)
            else:
                classIDList = result[0]['classID']
                sql = "SELECT * FROM classSchedule WHERE classID={classIDList} AND tutorID IS NULL".format(
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
                classDict[details['classID']] = [details['subject'], details['grade']]
            return jsonify(
                {
                    "scheduleList": scheduleList,
                    "classDict": classDict,
                    "code": 201
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

@app.route('/getClassTutors', methods=['GET'])
def getClassTutors():
    grade = request.args.get('grade')
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
    scheduleList = []
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
            relevantSchedules = [i['classID'] for i in result if i['grade']==grade]
            if (len(relevantSchedules) > 1):
                relevantSchedules = tuple(relevantSchedules)
                sql = "SELECT * from classSchedule WHERE classID IN {relevantSchedules} AND tutorID IS NOT NULL".format(relevantSchedules=relevantSchedules)
            else:
                relevantSchedules = relevantSchedules[0]
                sql = "SELECT * from classSchedule WHERE classID={relevantSchedules} AND tutorID IS NOT NULL".format(relevantSchedules=relevantSchedules)
            cursor.execute(sql)
            scheduleList = cursor.fetchall()
            tutorList = list(set([i['tutorID'] for i in scheduleList]))
            return jsonify(
                {
                    'classDict': classDict,
                    'tutorList': tutorList,
                    'scheduleList': scheduleList
                }
            )

@app.route('/getClassPrice', methods=['GET'])
def getClassPrice():
    classID = request.args.get('classID')
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            sql = "USE classScheduleDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT tuitionFee FROM Class WHERE classID={classID}".format(classID=classID)
            cursor.execute(sql)
            result = cursor.fetchall()
            return jsonify(result[0])
        
@app.route('/enrollStudent', methods=['POST'])
def enrollStudent():
    data = request.get_json()
    studentID = data['studentID']
    scheduleID = data['scheduleID']
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            sql = "USE classScheduleDB"
            cursor.execute(sql)
            connection.commit()
            cursor.execute(f"""INSERT INTO classScheduleStudent (studentID, scheduleID) VALUES (%s, %s)""", (studentID, scheduleID))
            connection.commit()
            return jsonify(
                {
                    'code': 201,
                    "message": 'Student has been successfully enrolled into class schedule.'
                }
            )

@app.route('/getStudentSchedule', methods=['GET'])
def getStudentSchedule():
    data = request.args.getlist('bookedSchedules')
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
    scheduleList = []
    classDict = {}
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = "USE classScheduleDB"
                cursor.execute(sql)
                connection.commit()
                if (len(data) > 1):
                    bookedSchedules = tuple([int(i) for i in data])
                    sql = "SELECT * FROM classSchedule WHERE scheduleID IN {}".format(bookedSchedules)
                else:
                    bookedSchedules = int(data[0])
                    sql = "SELECT * FROM classSchedule WHERE scheduleID={}".format(bookedSchedules)
                cursor.execute(sql)
                scheduleList = cursor.fetchall()
                sql = "SELECT classID, subject, grade FROM Class"
                cursor.execute(sql)
                result = cursor.fetchall()
                classDict = {i['classID']: [i['subject'], i['grade']]
                            for i in result}
                return jsonify(
                    {
                        "code": 201,
                        "scheduleList": scheduleList,
                        "classDict": classDict
                    }
                )
    except:
        return jsonify(
                    {
                        "code": 404,
                        "message": "Error, please contact administrator"
                    }
                )

@app.route('/getStudentList', methods=['GET'])
def getStudentList():
    scheduleID = int(request.args.get('scheduleID'))
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            sql = "USE classScheduleDB"
            cursor.execute(sql)
            connection.commit()
            sql = """SELECT classScheduleStudent.studentID
                    FROM classSchedule
                    JOIN classScheduleStudent
                    ON classSchedule.scheduleID = classScheduleStudent.scheduleID
                    WHERE classScheduleStudent.scheduleID={}""".format(scheduleID)
            cursor.execute(sql)
            result = cursor.fetchall()
            studentList = [i['studentID'] for i in result]
            return jsonify(
                {
                    "studentList": studentList
                }
            )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)

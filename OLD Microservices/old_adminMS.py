import pymysql.cursors
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import hashlib
import jwt

# instantiate flask app
app = Flask(__name__)

# enables cross-origin resource sharing for fetch apis
CORS(app)

# Set secret key
key = os.urandom(12)
app.config['SECRET_KEY'] = key

def validateToken(token):
    try:
        decoded = jwt.decode(
                            token,
                            app.config.get('SECRET_KEY'),
                            algorithms = ["HS256"]
                        )
        return {
            'status': True
        }
    except jwt.ExpiredSignatureError:
        return {
            'status': False,
            'error': 'Signature expired. Please log in again.'
        }
    except jwt.InvalidTokenError:
        return {
            'status': False,
            'error': 'Invalid token. Please log in again.'
        }
    
@app.route('/adminLogin', methods=['GET'])
def adminLogin():
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            email = request.args.get('email')
            password = request.args.get('pass')
            sql = "USE tutorDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT password FROM tutor WHERE email='{email}' AND isAdmin=1".format(email=email)
            cursor.execute(sql)
            results = cursor.fetchall()
            if (len(results) > 0):
                get_salt = results[0]['password'][:32]
                get_key = results[0]['password'][32:]
                new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), get_salt, 100000)
                if (new_key == get_key): 
                    payload =   {
                        "exp": datetime.utcnow() + timedelta(minutes = 5)
                    }
                    token = jwt.encode(
                        payload,
                        app.config.get('SECRET_KEY'),
                        algorithm = "HS256"
                    )
                    return jsonify(
                        {   
                            'token': token,
                            'status': True
                        }
                    )
                else:
                    return jsonify(
                        {   
                            'status': False
                        }
                    )
            else:
                return jsonify(
                        {   
                            'status': False
                        }
                    )

@app.route('/getPendingTutors', methods=['GET'])
def getPendingTutors():
    token = request.args.get('token')
    validation = validateToken(token)
    if (validation['status']):
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                sql = "USE tutorDB"
                cursor.execute(sql)
                connection.commit()
                sql = "SELECT firstName, lastName, email, phoneNumber, eduLevel, taughtSubjects, execSummary FROM tutor WHERE isApproved=0 AND isAdmin=0"
                cursor.execute(sql)
                tutorList = cursor.fetchall()
                return jsonify(
                    {
                        "data": {
                            "tutorList": tutorList
                        }
                    }
                )

@app.route('/approveTutor', methods=['PATCH'])
def approveTutor():
    data = request.get_json()
    token = data['token']
    validation = validateToken(token)
    if (validation['status']):
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                email = data['email']
                sql = "USE tutorDB"
                cursor.execute(sql)
                connection.commit()
                sql = "UPDATE tutor SET isApproved=1 WHERE email='{email}'".format(email=email)
                cursor.execute(sql)
                connection.commit()
                return data

@app.route('/rejectTutor', methods=['DELETE'])
def rejectTutor():
    data = request.get_json()
    token = data['token']
    validation = validateToken(token)
    if (validation['status']):
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                email = data['email']
                sql = "USE tutorDB"
                cursor.execute(sql)
                connection.commit()
                sql = "DELETE FROM tutor WHERE email='{email}'".format(email=email)
                cursor.execute(sql)
                connection.commit()
                return data

@app.route('/getApprovedTutors', methods=['GET'])
def getApprovedTutors():
    token = request.args.get('token')
    validation = validateToken(token)
    if (validation['status']):
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                sql = "USE tutorDB"
                cursor.execute(sql)
                connection.commit()
                sql = "SELECT firstName, lastName, email, phoneNumber, eduLevel, taughtSubjects, execSummary FROM tutor WHERE isApproved=1 AND isAdmin=0"
                cursor.execute(sql)
                tutorList = cursor.fetchall()
                return jsonify(
                    {
                        "data": {
                            "tutorList": tutorList
                        }
                    }
                )

@app.route('/getClassDetails', methods=['GET'])
def getClassDetails():
    token = request.args.get('token')
    validation = validateToken(token)
    if (validation['status']):
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                sql = "USE classDB"
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
    data = request.get_json()
    token = data['token']
    validation = validateToken(token)
    if (validation['status']): 
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
                sql = "USE classDB"
                cursor.execute(sql)
                connection.commit()
                classIDList = []
                for subject in chosenSubjects:
                    for grade in chosenGrades:
                        sql = "SELECT classID FROM Class WHERE subject='{subject}' and grade='{grade}'".format(subject=subject, grade=grade)
                        cursor.execute(sql)
                        result = cursor.fetchall()
                        classIDList.append(result[0]['classID'])
                sql = "USE classScheduleDB"
                cursor.execute(sql)
                connection.commit()
                for classID in classIDList:
                    for year in chosenYears:
                        for day in chosenDays:
                            for timing in chosenTimings:
                                sql = "INSERT INTO classSchedule (classID, year, day, timing) VALUES ({classID}, {year}, '{day}', {timing})".format(classID=classID, year=year, day=day, timing=timing)
                                cursor.execute(sql)
                                connection.commit()
                return data
 
@app.route('/getClassSchedules', methods=['GET'])
def getClassSchedules():
    token = request.args.get('token')
    validation = validateToken(token)
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
                sql = "USE classDB"
                cursor.execute(sql)
                connection.commit()
                sql = "SELECT classID, subject, grade FROM Class"
                cursor.execute(sql)
                result = cursor.fetchall()
                for details in result:
                    classDict[details['classID']] = [details['subject'], details['grade']]
                return jsonify(
                    {
                        "data": {
                            "scheduleList": scheduleList,
                            "classDict": classDict
                        }
                    }
                )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
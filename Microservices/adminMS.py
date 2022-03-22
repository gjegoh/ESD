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
        
# functionality 5: (tutorLogin.html) Authenticates tutor 
@app.route('/adminLogout', methods=['GET'])
def adminLogout():
    key = os.urandom(12)
    app.config['SECRET_KEY'] = key
    
# functionality 5: (tutorLogin.html) Authenticates tutor 
@app.route('/adminLogin', methods=['GET'])
def adminLogin():
    # retrieves data of GET request from tutorLogin.html, in json
    # connects to RDS
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            # processes data of GET request
            email = request.args.get('email')
            password = request.args.get('pass')
            # accesses tutorDB to get salt+key
            sql = "USE tutorDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT password FROM tutor WHERE email='{email}' AND isAdmin=1".format(email=email)
            cursor.execute(sql)
            results = cursor.fetchall()
            # if tutor is authenticated, returns status of authentication and tutorID
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

# functionality 1: (adminViewPendingTutors.html) Gets all tutors with isApproved=0, aka 
# pending tutors via GET request to tutorDB
@app.route('/getPendingTutors', methods=['GET'])
def getPendingTutors():
    token = request.args.get('token')
    validation = validateToken(token)
    if (validation['status']):
        # connects to RDS
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                # accesses tutorDB to retrieve all tutor's details
                sql = "USE tutorDB"
                cursor.execute(sql)
                connection.commit()
                sql = "SELECT firstName, lastName, email, phoneNumber, eduLevel, taughtSubjects, execSummary FROM tutor WHERE isApproved=0 AND isAdmin=0"
                cursor.execute(sql)
                tutorList = cursor.fetchall()
                # sends data via response back to adminViewPendingTutors.html, in json
                return jsonify(
                    {
                        "data": {
                            "tutorList": tutorList
                        }
                    }
                )

# functionality 2: (adminViewPendingTutors.html) Updates isApproved=1 for selected tutor 
# via PATCH request to tutorDB
@app.route('/approveTutor', methods=['PATCH'])
def approveTutor():
    # retrieves data of PATCH request from adminViewPendingTutors.html, in json
    data = request.get_json()
    token = data['token']
    validation = validateToken(token)
    if (validation['status']):
        # connects to RDS
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                # processes data from PATCH request
                email = data['email']
                # accesses tutorDB 
                sql = "USE tutorDB"
                cursor.execute(sql)
                connection.commit()
                # updates selected tutor to be approved
                sql = "UPDATE tutor SET isApproved=1 WHERE email='{email}'".format(email=email)
                cursor.execute(sql)
                connection.commit()
                # sends received data from PATCH request, via response back to
                # adminViewPendingTutors in json
                return data

# functionality 3: (adminViewPendingTutors.html) Deletes selected tutor
# via DELETE request to tutorDB
@app.route('/rejectTutor', methods=['DELETE'])
def rejectTutor():
    # retrieves data of DELETE request from adminViewPendingTutors.html, in json
    data = request.get_json()
    token = data['token']
    validation = validateToken(token)
    if (validation['status']):
        # connects to RDS
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                # processes data of DELETE request
                email = data['email']
                # accesses tutorDB to delete selected tutor
                sql = "USE tutorDB"
                cursor.execute(sql)
                connection.commit()
                sql = "DELETE FROM tutor WHERE email='{email}'".format(email=email)
                cursor.execute(sql)
                connection.commit()
                # sends received data from DELETE request, via response back to
                # adminViewPendingTutors in json
                return data

# functionality 4: (adminViewPendingTutors.html) Gets all tutors with isApproved=1, aka 
# approved tutors via GET request to tutorDB
@app.route('/getApprovedTutors', methods=['GET'])
def getApprovedTutors():
    token = request.args.get('token')
    validation = validateToken(token)
    if (validation['status']):
        # connects to RDS
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                # accesses tutorDB to retrieve all tutor's details
                sql = "USE tutorDB"
                cursor.execute(sql)
                connection.commit()
                sql = "SELECT firstName, lastName, email, phoneNumber, eduLevel, taughtSubjects, execSummary FROM tutor WHERE isApproved=1 AND isAdmin=0"
                cursor.execute(sql)
                tutorList = cursor.fetchall()
                # sends data via response back to adminViewPendingTutors.html, in json
                return jsonify(
                    {
                        "data": {
                            "tutorList": tutorList
                        }
                    }
                )


# functionality 1: (adminCreateSchedules.html) Gets "fixe d" class details to populate form
# details via GET request to classDB
@app.route('/getClassDetails', methods=['GET'])
def getClassDetails():
    token = request.args.get('token')
    validation = validateToken(token)
    if (validation['status']):
        # connects to RDS
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                # access classDB to retrieve list of all unique subjects/grades
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
                # sends data via response back to adminCreateSchedules.html, in json
                return jsonify(
                    {
                        "data": {
                            "subject": subjectList,
                            "grade": gradeList
                        }
                    }
                )

# functionality 2: (adminCreateSchedules.html) Creates class schedules based on user input
# via POST request to classScheduleDB
@app.route('/createClassSchedule', methods=['POST'])
def createClassSchedule():
    # receives data of POST request from adminCreateSchedules.html, in json
    data = request.get_json()
    token = data['token']
    validation = validateToken(token)
    if (validation['status']):
        # connects to RDS 
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                # processes data from POST request
                chosenSubjects = data['subjects']
                chosenGrades = data['grades']
                chosenYears = data['years']
                chosenDays = data['days']
                chosenTimings = data['timings']
                # accesses classDB to get list of unique corresponding classID 
                # of subject/grade combination
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
                # accesses classScheduleDB to create new class schedule based on received data 
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
                # sends received data from POST request, via response back to
                # adminCreateSchedules in json
                return data

# functionality 3: (adminViewSchedules.html) Gets all class schedules to populate table
# via GET request to classDB (to retrieve subjects/grades based on classID) and to 
# classScheduleDB  
@app.route('/getClassSchedules', methods=['GET'])
def getClassSchedules():
    token = request.args.get('token')
    validation = validateToken(token)
    if (validation['status']):
        # connects to RDS
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
        # gets list of all class schedules via GET request to classScheduleDB
        # and creates dictionary, mapping classID to corresponding subject/grade
        # combination
        scheduleList = []
        classDict = {}
        with connection:
            with connection.cursor() as cursor:
                # accesses classScheduleDB to get all class schedules
                sql = "USE classScheduleDB"
                cursor.execute(sql)
                connection.commit()
                sql = "SELECT * FROM classSchedule"
                cursor.execute(sql)
                scheduleList = cursor.fetchall()
                # accesses classDB to get all classID with its corresponding unique
                # subject/grade combination
                sql = "USE classDB"
                cursor.execute(sql)
                connection.commit()
                sql = "SELECT classID, subject, grade FROM Class"
                cursor.execute(sql)
                result = cursor.fetchall()
                for details in result:
                    classDict[details['classID']] = [details['subject'], details['grade']]
                # sends data via response back to adminViewSchedules.html, in json
                return jsonify(
                    {
                        "data": {
                            "scheduleList": scheduleList,
                            "classDict": classDict
                        }
                    }
                )

# runs flask app (host 0.0.0.0 makes app available for all PCs on SAME network)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
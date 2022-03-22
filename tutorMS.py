import pymysql.cursors
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import hashlib

# instantiate flask app
app = Flask(__name__)

# enables cross-origin resource sharing for fetch apis
CORS(app)

# functionality 1: (adminViewPendingTutors.html) Gets all tutors with isApproved=0, aka 
# pending tutors via GET request to tutorDB
@app.route('/getPendingTutors', methods=['GET'])
def getPendingTutors():
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
            sql = "SELECT firstName, lastName, email, phoneNumber, eduLevel, taughtSubjects, execSummary FROM tutor WHERE isApproved=0"
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
            sql = "SELECT firstName, lastName, email, phoneNumber, eduLevel, taughtSubjects, execSummary FROM tutor WHERE isApproved=1"
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

# functionality 5: (tutorLogin.html) Authenticates tutor 
@app.route('/tutorLogin', methods=['GET'])
def tutorLogin():
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
            sql = "SELECT password, tutorID FROM tutor WHERE email='{email}' AND isApproved=1".format(email=email)
            cursor.execute(sql)
            results = cursor.fetchall()
            # if tutor is authenticated, returns status of authentication and tutorID
            if (len(results) > 0):
                get_salt = results[0]['password'][:32]
                get_key = results[0]['password'][32:]
                tutorID = results[0]['tutorID']
                new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), get_salt, 100000)
                if (new_key == get_key): 
                    return jsonify(
                        {
                            "status": True,
                            "tutorID": tutorID
                        }
                    )
                else:
                    return jsonify(
                        {
                            "status": False
                        }
                    )
            else:
                return jsonify(
                        {
                            "status": False
                        }
                    )

# functionality 6: (tutorViewPendingSchedules.html) Gets all schedules compatible with current tutor
# and no current assigned tutors 
@app.route('/getUnassignedClasses', methods=['GET'])
def getUnassignedClasses():
    # processes data of GET request
    tutorID = int(request.args.get('tutorID'))
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
            # accesses tutorDB to get education level and taught subjects of current tutor
            sql = "USE tutorDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT eduLevel, taughtSubjects FROM tutor WHERE tutorID={tutorID}".format(tutorID=tutorID)
            cursor.execute(sql)
            result = cursor.fetchall()
            eduLevel = result[0]['eduLevel']
            taughtSubjects = tuple(result[0]['taughtSubjects'].split(','))
            # accesses classDB to get all classIDs of compatible classes with current tutor
            sql = "USE classDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT classID, subject, grade FROM Class WHERE grade LIKE '{eduLevel}%' AND subject IN {taughtSubjects}".format(eduLevel=eduLevel, taughtSubjects=taughtSubjects)
            cursor.execute(sql)
            result = cursor.fetchall()
            classIDList = tuple([i['classID'] for i in result])
            classDict = {i['classID']: [i['subject'], i['grade']] for i in result}
            # accesses classScheduleDB to get unassigned class schedules with classIDs
            sql = "USE classScheduleDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT * FROM classSchedule WHERE classID IN {classIDList} AND tutorID IS NULL".format(classIDList=classIDList)
            cursor.execute(sql)
            scheduleList = cursor.fetchall()
            # sends data via response back to tutorViewSchedules.html, in json
            return jsonify(
                {
                    "scheduleList": scheduleList,
                    "classDict": classDict
                }
            )

# functionality 7: (tutorViewPendingSchedules.html) Updates chosen schedule with current tutor ID
@app.route('/registerClass', methods=['PATCH'])
def registerClass():
    # retrieves data of PATCH request from adminViewPendingTutors.html, in json
    data = request.get_json()
    # connects to RDS
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            # processes data from PATCH request
            scheduleID = data['scheduleID']
            tutorID = data['tutorID']
            # accesses tutorDB 
            sql = "USE classScheduleDB"
            cursor.execute(sql)
            connection.commit()
            # updates selected tutor to be approved
            sql = "UPDATE classSchedule SET tutorID={tutorID} WHERE scheduleID={scheduleID}".format(tutorID=tutorID, scheduleID=scheduleID)
            cursor.execute(sql)
            connection.commit()
            # sends received data from PATCH request, via response back to
            # adminViewPendingTutors in json
            return data

# functionality 6: (tutorViewOwnSchedules.html) Gets all schedules taken by current tutor
@app.route('/getMySchedule', methods=['GET'])
def getMySchedule():
    # processes data of GET request
    tutorID = int(request.args.get('tutorID'))
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
            # accesses classScheduleDB to get unassigned class schedules with classIDs
            sql = "USE classScheduleDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT * FROM classSchedule WHERE tutorID={tutorID}".format(tutorID=tutorID)
            cursor.execute(sql)
            scheduleList = cursor.fetchall()
            # accesses classDB to get dict of classIDs to its corresponding grade/subject
            sql = "USE classDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT classID, subject, grade FROM Class"
            cursor.execute(sql)
            result = cursor.fetchall()
            classDict = {i['classID']: [i['subject'], i['grade']] for i in result}
            # sends data via response back to tutorViewSchedules.html, in json
            return jsonify(
                {
                    "scheduleList": scheduleList,
                    "classDict": classDict
                }
            )

# runs flask app (host 0.0.0.0 makes app available for all PCs on SAME network)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
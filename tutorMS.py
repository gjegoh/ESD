import pymysql.cursors
from flask import Flask, request, jsonify
from flask_cors import CORS

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
            # accesses tutorDB and updates selected tutor to be approved
            sql = "USE tutorDB"
            cursor.execute(sql)
            connection.commit()
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

# runs flask app (host 0.0.0.0 makes app available for all PCs on SAME network)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
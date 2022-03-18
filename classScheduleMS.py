import pymysql.cursors
from flask import Flask, request, jsonify
from flask_cors import CORS

# instantiate flask app
app = Flask(__name__)

# enables cross-origin resource sharing for fetch apis
CORS(app)

# functionality 1: (adminCreateSchedules.html) Gets "fixed" class details to populate form
# details via GET request to classDB
@app.route('/getClassDetails', methods=['GET'])
def getClassDetails():
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
    app.run(host='0.0.0.0', port=5001)
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

key = os.urandom(12)
app.config['SECRET_KEY'] = key
  
@app.route('/validateToken', methods=['GET'])
def validateToken():
    token = request.args.get('token')
    try:
        decoded = jwt.decode(
                            token,
                            app.config.get('SECRET_KEY'),
                            algorithms = ["HS256"]
                        )
        return {
            'code': 201,
            'token': decoded
        }
    except jwt.ExpiredSignatureError:
        return {
            'code': 403,
            'error': 'Signature expired. Please log in again.'
        }
    except jwt.InvalidTokenError:
        return {
            'code': 403,
            'error': 'Invalid token. Please log in again.'
        }

@app.route('/studentLogin', methods=['GET'])
def studentLogin():
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            email = request.args.get('email')
            password = request.args.get('password')
            sql = "USE studentDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT password, student_id, grade FROM student WHERE email='{email}'".format(email=email)
            cursor.execute(sql)
            results = cursor.fetchall()
            if (len(results) > 0):
                get_salt = results[0]['password'][:32]
                get_key = results[0]['password'][32:]
                studentID = results[0]['student_id']
                grade = results[0]['grade']
                new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), get_salt, 100000)
                if (new_key == get_key): 
                    payload =   {
                        "studentID": studentID,
                        "grade": grade,
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
                            'code': 201,
                        }
                    )
                else:
                    return jsonify(
                        {   
                            'code': 401,
                        }
                    )
            else:
                return jsonify(
                        {   
                            'code': 403,
                        }
                    )

@app.route("/studentRegister", methods=['POST'])
def studentRegister():
    data = request.get_json()
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection:
            with connection.cursor() as cursor:
                firstName = data['firstName']
                lastName = data['lastName']
                email = data['email']
                grade = data['grade']
                phoneNumber = data['phoneNumber']
                password = data['password']
                salt = os.urandom(32)
                key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
                hashedpass = salt + key
                sql = "USE studentDB"
                cursor.execute(sql)
                connection.commit()
                cursor.execute(f"""INSERT INTO student (firstName, lastName, email, grade, phoneNumber, password) VALUES (%s, %s, %s, %s, %s, %s)""", (firstName, lastName, email, grade, phoneNumber, hashedpass))
                connection.commit()
                return jsonify(
                    {
                        'code': 201,
                    }
                )
    except:
        return jsonify(
                    {
                        'code': 500,
                        'message': 'This email address is used. Please try another email address.'
                    }
                )
        
            
@app.route('/getClassesBooked', methods=['GET'])
def getClassesBooked():
    studentID = int(request.args.get('studentID'))
    bookedSchedules = []
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = "USE studentDB"
                cursor.execute(sql)
                connection.commit()
                sql = """SELECT studentBookedSchedules.scheduleID
                            FROM student
                            JOIN studentBookedSchedules
                            ON student.student_id = studentBookedSchedules.studentID
                            WHERE studentBookedSchedules.studentID = {}""".format(studentID)
                cursor.execute(sql)
                results = cursor.fetchall()
                for result in results:
                    bookedSchedules.append(result['scheduleID'])
                return jsonify(
                    {   
                        'code':201,
                        'bookedSchedules': bookedSchedules
                    }
                )
    except:
        return jsonify(
                {   
                    'code':500,
                    'message':"Database error, please contact administrator."
                }
            )

@app.route('/updateStudentBooking', methods=['POST'])
def updateStudentBooking():
    data = request.get_json()
    scheduleID = data['scheduleID']
    studentID = data['studentID']
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            sql = "USE studentDB"
            cursor.execute(sql)
            connection.commit()
            cursor.execute(f"""INSERT INTO studentBookedSchedules (studentID, scheduleID) VALUES (%s, %s)""", (studentID, scheduleID))
            connection.commit()
            return jsonify(
                {
                    'code': 201,
                }
            )
            
@app.route('/getStudentNames', methods=['GET'])
def getStudentNames():
    data = request.args.getlist('studentList')
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            sql = "USE studentDB"
            cursor.execute(sql)
            connection.commit()
            if (len(data) == 0):
                # if there is no data
                return jsonify([])
            else:
                if (len(data) > 1):
                    studentList = tuple([int(i) for i in data])
                    sql = "SELECT student_id, firstName, lastName FROM student WHERE student_id IN {studentList}".format(studentList=studentList)
                elif (len(data) == 1):
                    studentList = int(data[0])
                    sql = "SELECT student_id, firstName, lastName FROM student WHERE student_id={studentList}".format(studentList=studentList)
                cursor.execute(sql)
                result = cursor.fetchall()
            return jsonify(
                {
                    "code": 201,
                    "data": result
                    
                }
            )
            

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
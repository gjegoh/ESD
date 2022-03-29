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

@app.route('/manageTutor', methods=['PATCH', 'DELETE'])
def manageTutor():
    try:
        data = request.args
        connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                    user='admin',
                                    password='thisismypw',
                                    cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                email = data['email']
                action = data['action']
                sql = "USE tutorDB"
                cursor.execute(sql)
                connection.commit()
                if (action == "approve"):
                    sql = "UPDATE tutor SET isApproved=1 WHERE email='{email}'".format(email=email)
                else:
                    sql = "DELETE FROM tutor WHERE email='{email}'".format(email=email)
                cursor.execute(sql)
                connection.commit()
                return jsonify(
                    {
                        'status': True
                    }
                )
    except pymysql.Error:
        return jsonify(
            {
                'status': False
            }
        )

@app.route('/getPendingTutors', methods=['GET'])
def getPendingTutors():
    token = request.args.get('token')
    payload = {'token': token}
    # url = "http://10.124.9.182:5000/validateToken"
    url = "http://10.124.141.82:5003/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
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

@app.route('/getApprovedTutors', methods=['GET'])
def getApprovedTutors():
    token = request.args.get('token')
    payload = {'token': token}
    # url = "http://10.124.9.182:5000/validateToken"
    url = "http://10.124.141.82:5003/validateToken"
    response = requests.get(url, params=payload)
    validation = response.json()
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
            'status': True,
            'token': decoded
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

@app.route('/tutorLogin', methods=['GET'])
def tutorLogin():
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            email = request.args.get('email')
            password = request.args.get('password')
            sql = "USE tutorDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT password, tutorID FROM tutor WHERE email='{email}' AND isApproved=1".format(email=email)
            cursor.execute(sql)
            results = cursor.fetchall()
            if (len(results) > 0):
                get_salt = results[0]['password'][:32]
                get_key = results[0]['password'][32:]
                tutorID = results[0]['tutorID']
                new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), get_salt, 100000)
                if (new_key == get_key): 
                    payload =   {
                        "tutorID": tutorID,
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

@app.route("/tutorRegister", methods=['POST'])
def tutorRegister():
    data = request.get_json()
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            firstName = data['firstName']
            lastName = data['lastName']
            email = data['email']
            eduLevel = data['eduLevel']
            taughtSubjects = data['taughtSubjects']
            phoneNumber = data['phoneNumber']
            execSummary = data['execSummary']
            password = data['password']
            salt = os.urandom(32)
            key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            hashedpass = salt + key
            sql = "USE tutorDB"
            cursor.execute(sql)
            connection.commit()
            cursor.execute(f"""INSERT INTO tutor (firstName, lastName, email, eduLevel, taughtSubjects, phoneNumber, execSummary, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (firstName, lastName, email, eduLevel, taughtSubjects, phoneNumber, execSummary, hashedpass))
            connection.commit()
            return jsonify(
                {
                    'status': True
                }
            )
            
@app.route("/getTutorInfo", methods=['GET'])
def getTutorInfo():
    tutorID = request.args.get('tutorID')
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                                user='admin',
                                password='thisismypw',
                                cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            sql = "USE tutorDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT eduLevel, taughtSubjects FROM tutor WHERE tutorID={tutorID}".format(tutorID=tutorID)
            cursor.execute(sql)
            result = cursor.fetchall()
            return result[0]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
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
    url = "http://10.124.9.182:5000/validateToken"
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
    url = "http://10.124.9.182:5000/validateToken"
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
                
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
import os
import hashlib

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/book'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:thisismypw@studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com:3306/studentDB'
# using additional schema, can add more in the {}
app.config['SQLALCHEMY_BINDS'] = {'class':'mysql+mysqlconnector://admin:thisismypw@studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com:3306/classDB'}
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)


class Student(db.Model):
    __tablename__ = 'student'
    
    student_id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(64), nullable=False)
    lastName = db.Column(db.String(64), nullable=False)
    grade = db.Column(db.Integer)
    email = db.Column(db.String(64), nullable=False)
    phoneNumber = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(64), nullable=False)

    # def __init__(self, student_id, firstName, lastName, grade, email, phoneNumber, password):
    #     self.student_id = student_id
    #     self.firstName = firstName
    #     self.lastName = lastName
    #     self.grade = grade
    #     self.email = email
    #     self.phoneNumber = phoneNumber
    #     self.password = password

    def json(self):
        return {"student_id": self.student_id, "firstName": self.firstName, "lastName": self.lastName, "grade": self.grade, "email": self.email, "phoneNumber": self.phoneNumber}

class EducationInfo(db.Model):
    #binding the second schema (classDB)
    __bind_key__ = 'class'
    __tablename__ = 'educationInfo'
    
    id = db.Column(db.Integer, primary_key=True)
    educationLevel = db.Column(db.String(45), nullable=False)
    level = db.Column(db.String(45), nullable=False)

    def json(self):
        return {"id": self.id, "educationLevel": self.educationLevel, "level": self.level}

@app.route("/student")
def get_all():
    studentlist = Student.query.all()
    if len(studentlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "students": [student.json() for student in studentlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no students."
        }
    ), 404

@app.route("/student", methods=['POST'])
def register_student():
    
    # retrieve the whole javascript object; {xxx:yyy}
    data = request.get_json()
    
    firstName = data['firstName']
    lastName = data['lastName']
    email = data['email']
    grade = data['grade']
    phoneNumber = data['phoneNumber']
    password = data['password']
    # generates salt, random password and then hashes it, [:32] is salt, [32:] is hash
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    hashedpass = salt + key
    student = Student(firstName=firstName, lastName=lastName, email=email, grade=grade, phoneNumber=phoneNumber, password=hashedpass)

    try:
        db.session.add(student)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the order. " + str(e)
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": student.json()
        }
    ), 201

@app.route("/educationInfo/<string:educationLevel>")
def get_educationLevel(educationLevel):
    educationList = EducationInfo.query.filter_by(educationLevel=educationLevel)

    # educationList = EducationInfo.query.all()
    if educationList:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "educationLevels": [education.json() for education in educationList]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no results."
        }
    ), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
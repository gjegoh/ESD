from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
import os
import hashlib

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/book'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:thisismypw@studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com:3306/tutorDB'
# using additional schema, can add more in the {}
app.config['SQLALCHEMY_BINDS'] = {'subject':'mysql+mysqlconnector://admin:thisismypw@studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com:3306/classDB'}
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)


class Tutor(db.Model):
    __tablename__ = 'tutor'

    tutorID = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(45), nullable=False)
    lastName = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    eduLevel = db.Column(db.String(45), nullable=False)
    taughtSubjects = db.Column(db.String(200), nullable=False)
    execSummary = db.Column(db.String(250))
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
        return {"tutorID": self.tutorID, "firstName": self.firstName, "lastName": self.lastName, 
        "email": self.email,"eduLevel": self.eduLevel,"taughtSubjects": self.taughtSubjects, 
        "execSummary": self.execSummary, "phoneNumber": self.phoneNumber, }

class SubjectInfo(db.Model):
    #binding the second schema (subject)
    __bind_key__ = 'subject'
    __tablename__ = 'subjectInfo'
    
    subjectInfo_id = db.Column(db.Integer, primary_key=True)
    educationLevel = db.Column(db.String(45), nullable=False)
    subject = db.Column(db.String(45), nullable=False)

    def json(self):
        return {"id": self.subjectInfo_id, "educationLevel": self.educationLevel, "subject": self.subject}

@app.route("/tutor")
def get_all():
    tutorList = Tutor.query.all()
    if len(tutorList):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "tutors": [tutor.json() for tutor in tutorList]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no tutors."
        }
    ), 404


@app.route("/tutor", methods=['POST'])
def register_student():

    # retrieve the whole javascript object; {xxx:yyy}
    data = request.get_json()
    print(data)
    firstName = data['firstName']
    lastName = data['lastName']
    email = data['email']
    eduLevel = data['eduLevel']
    taughtSubjects = data['taughtSubjects']
    phoneNumber = data['phoneNumber']
    execSummary = data['execSummary']
    password = data['password']
    # generates salt, random password and then hashes it, [:32] is salt, [32:] is hash
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    hashedpass = salt + key
    tutor = Tutor(firstName=firstName, lastName=lastName, email=email,eduLevel=eduLevel,taughtSubjects=taughtSubjects,
                phoneNumber=phoneNumber, execSummary=execSummary, password=hashedpass)

    try:
        db.session.add(tutor)
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
            "data": tutor.json()
        }
    ), 201

@app.route("/subjectInfo/<string:educationLevel>")
def get_subject(educationLevel):
    subjectList = SubjectInfo.query.filter_by(educationLevel=educationLevel)

    if subjectList:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "educationLevels": [subject.json() for subject in subjectList]
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

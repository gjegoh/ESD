from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
 
app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/book'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:thisismypw@studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com:3306/studentDB'
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
    
    student = Student(firstName=firstName, lastName=lastName, email=email, grade=grade, phoneNumber=phoneNumber, password=password)

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
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)


# @app.route("/newStudentNotification", methods=['POST'])
# def newStudentNotification():
#     message = request.get_json()
#     data = json.dumps(message)
#     print("sending the data into queue")
#     amqp.channel.basic_publish(exchange=amqp.exchangename, routing_key="student.newStudent", 
#             body=data, properties=pika.BasicProperties(delivery_mode = 2)) 
    
#     return data

# @app.route("/newTutorNotification", methods=['POST'])
# def newTutorNotification():
#     message = request.get_json()
#     data = json.dumps(message)
#     print("sending the data into queue")
#     amqp.channel.basic_publish(exchange=amqp.exchangename, routing_key="tutor.newTutor", 
#             body=data, properties=pika.BasicProperties(delivery_mode = 2)) 
#     return data

@app.route("/approveTutorNotification", methods=['POST'])
def approveTutorNotification():
    message = request.get_json()
    # message = {"email": "studenttuitioncentre1@gmail.com"}
    data = json.dumps(message)
    #send the data into queue
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="tutor.approveTutor", 
            body=data, properties=pika.BasicProperties(delivery_mode = 2)) 
    return data

@app.route("/rejectTutorNotification", methods=['POST'])
def rejectTutorNotification():
    message = request.get_json()
    # message = {"email": "studenttuitioncentre1@gmail.com"}
    data = json.dumps(message)
    #send the data into queue
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="tutor.rejectTutor", 
            body=data, properties=pika.BasicProperties(delivery_mode = 2)) 
    return data

# @app.route("/newClassScheduleNotification", methods=['POST'])
# def newClassScheduleNotification():
#     message = request.get_json()
#     data = json.dumps(message)
#     amqp.channel.basic_publish(exchange=amqp.exchangename, routing_key="class.newClassSchedule", 
#             body=data, properties=pika.BasicProperties(delivery_mode = 2)) 
#     return data

@app.route("/paymentSuccessfulNotification", methods=['POST'])
def paymentSuccessfulNotification():
    # message = {
    #     'paymentEmail': "ffdad@gmail.com",
    #     'paymentID': "12345",
    #     'paymentAmount': "45.06",
    #     'paymentDatetime': "3 April 2022",
    #     'paymentStatus': "successful"
    # }
    message = request.get_json()
    data = json.dumps(message)
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="payment.paymentSuccessful", 
            body=data, properties=pika.BasicProperties(delivery_mode = 2)) 
    return data

if __name__ == '__main__':
    print("This is flask " + os.path.basename(__file__) + " for sending an notification...")
    app.run(host="0.0.0.0", port=5010, debug=True)
import pymysql.cursors
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from datetime import datetime, timedelta
import requests
import os
import hashlib
import jwt
import stripe
import time  

# instantiate flask app
app = Flask(__name__)

# enables cross-origin resource sharing for fetch apis
CORS(app)
    
@app.route('/logTransaction', methods=['POST'])
def logTransaction():
    data = request.get_json()
    paymentEmail = data['paymentEmail']
    paymentID = data['paymentID']
    paymentAmount = data['paymentAmount']
    paymentDatetime = data['paymentDatetime']
    paymentStatus = data['paymentStatus']
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                        user='admin',
                        password='thisismypw',
                        cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            sql = "USE transactionDB"
            cursor.execute(sql)
            connection.commit()
            cursor.execute(f"""INSERT INTO transaction (paymentEmail, paymentID, paymentAmount, paymentDatetime, paymentStatus) VALUES (%s, %s, %s, %s, %s)""", (paymentEmail, paymentID, paymentAmount, paymentDatetime, paymentStatus))
            connection.commit()
    return jsonify(
        {
            'code': 200,
            'message': 'Payment transaction is logged successfully.'
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)
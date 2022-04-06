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

app.config['STRIPE_PUBLIC_KEY'] = "pk_test_51KikEDLVS1n78x0ibCgvm23w7Jx5Cn2V74uubC6tMQsyOKjrA05R3DkotyKXT2v8QTkX8fvdxqtD0gDo3nTd1Ym400LGrwALZ1"
app.config['STRIPE_SECRET_KEY'] = "sk_test_51KikEDLVS1n78x0iu8FVBGGZVjfpkOuWjHvdmT4Y4R3yNMTrYxjiflKfzPTOuurYYf2zE4JA2LCUka4WGsCxuMBA00VBGA47wB"
stripe.api_key = app.config['STRIPE_SECRET_KEY']

paymentAPIkey= {
    1: 'price_1KjztxLVS1n78x0i3qaAb4Te',
    2: 'price_1KkC6wLVS1n78x0iJz2mTl3B',
    3: 'price_1KkC7GLVS1n78x0igpxfCIY5',
    4: 'price_1KkC7rLVS1n78x0iYItyU0rh',
    5: 'price_1KkC85LVS1n78x0iHWpe35Gk',
    6: 'price_1KkC8JLVS1n78x0iutLIzQjr',
    7: 'price_1KkC8tLVS1n78x0icsWGUsMe',
    8: 'price_1KkC94LVS1n78x0iuK2Si0BE',
    9: 'price_1KkC9FLVS1n78x0iWL6jkxqe'
}
    
@app.route('/stripePay', methods=['GET'])
def stripePay():
    token = request.args.get('token')
    studentID = int(request.args.get('studentID')) 
    classID = int(request.args.get('classID')) 
    scheduleID = int(request.args.get('scheduleID'))
    session = stripe.checkout.Session.create(
        line_items = [{
            'price': paymentAPIkey[classID],
            'quantity': 1
        }],
        metadata = {
            'scheduleID': scheduleID,
            'studentID': studentID
        },
        mode = 'payment',
        success_url = "http://127.0.0.1:5500/StudentUI/paymentSuccess.html?session_id={CHECKOUT_SESSION_ID}" + "&token={}".format(token),
        cancel_url = "http://127.0.0.1:5500/StudentUI/studentViewAvailableSchedules.html" + "&token={}".format(token)
    )
    return jsonify(
        {
            'checkout_session_id': session['id'],
            'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
        }
    )
    
@app.route('/stripeWebhook', methods=['POST'])
def stripeWebHook():
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    # generated from stripe CLI, docker might need change
    endpoint_secret = 'whsec_435a1e7d72f07b927dd1e79c114c4893521dcc961aa274867b7954bda9381f93'
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except stripe.error.SignatureVerificationError as e:
        return {}, 400
    if (event['type'] == 'checkout.session.completed'):
        session = event['data']['object']
        paymentID = session['payment_intent']
        paymentEmail = session['customer_details']['email']
        paymentAmount = session['amount_total']/100
        paymentDatetime = time.strftime('%Y-%m-%d %H:%M:%S')
        paymentStatus = session['payment_status']
        scheduleID = int(session['metadata']['scheduleID'])
        studentID = int(session['metadata']['studentID'])
        payload = {
            'paymentEmail': paymentEmail,
            'paymentID': paymentID,
            'paymentAmount': paymentAmount,
            'paymentDatetime': paymentDatetime,
            'paymentStatus': paymentStatus
        }
        url = "http://transaction:5007/logTransaction"
        response = requests.post(url, json=payload)
        data = response.json()
        payload = {
            'scheduleID': scheduleID,
            'studentID': studentID
        }
        url = "http://classSchedule:5004/enrollStudent"
        response = requests.post(url, json=payload)
        data = response.json()
        payload = {
            'scheduleID': scheduleID,
            'studentID': studentID
        }
        url = "http://student:5005/updateStudentBooking"
        response = requests.post(url, json=payload)
        data = response.json()
        #call notiMS using paymentEmail, amount, datatime, paymentid, status
        payload = {
            'paymentEmail': paymentEmail,
            'paymentID': paymentID,
            'paymentAmount': paymentAmount,
            'paymentDatetime': paymentDatetime,
            'paymentStatus': paymentStatus
        }
        paymentSuccessfulURL = "http://notification:5010/paymentSuccessfulNotification"
        response = requests.post(paymentSuccessfulURL, json=payload)
    return {}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
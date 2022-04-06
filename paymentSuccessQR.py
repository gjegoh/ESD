import json
import os
import amqp_setup
import mailchimpFunctions

from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
import pymysql.cursors
from mailchimp3 import MailChimp
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from urllib.parse import parse_qs
import time

app = Flask(__name__)

# enables cross-origin resource sharing for fetch apis
CORS(app)

monitorBindingKey='*.paymentSuccessful'

def receiveSuccessfulPayment():
    amqp_setup.check_setup()
    
    queue_name = "paymentSuccessful"  

    # set up a consumer and start to wait for coming messages
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived an successful payment by " + __file__)
    processPayment(body)
    print() # print a new line feed

def processPayment(body):
    print("Printing the successful payment message:")
    try:
        message = json.loads(body)
        print("--JSON:", message)
    except Exception as e:
        print("--NOT JSON:", e)
        print("--DATA:", body)
    print()
    #try the mailchimp api key
    #check whether the API key is valid
    #if successful, will return {"health_status": "Everything's Chimpy!"} 
    try:
        apiKeyStatus = 200
        client = MailchimpMarketing.Client()
        client.set_config({
            "api_key": "da0da6b72eff90471e10518dd42e8926",
            "server": "us14"
        })

        response = client.ping.get()
        print(response)
    except ApiClientError as error:
        apiKeyStatus = error['status']
        print("Error: {}".format(error.text))
    #create new contact
    if apiKeyStatus == 200:
        email = message['paymentEmail']
        paymentID = str(message['paymentID'])
        paymentAmount = str(message['paymentAmount'])
        paymentDateTime = str(message['paymentDatetime'])
        print("adding new contact")
        addNewStudentStatus, addNewStudentResponse = mailchimpFunctions.addContact(email)
        print(addNewStudentStatus)
        print(addNewStudentResponse)
        #add approved tutors into reject segment
        if addNewStudentStatus == 200:
            print("add student into payment segment:")
            segment_id, createSegmentStatus, createSegmentResponse = mailchimpFunctions.addMemberIntoSegment("payment", email)
            print(createSegmentStatus)
            print(createSegmentResponse)
            print(segment_id)
            #create campaign
            if createSegmentStatus == 200:
                campaign_name = "Successful payment"
                from_name = "Tuition Centre"
                reply_to = "esdtuitioncentre@gmail.com"
                print("Creating new user campaign:")
                campaign_id, createCampaignStatus, createCampaignResponse = mailchimpFunctions.createCampaign(campaign_name, from_name, reply_to, segment_id)
 
                print(campaign_id)
                print(createCampaignStatus)
                print(createCampaignResponse)
                #add content
                if createCampaignStatus == 200:
                    print("adding content")
                    addContentStatus, addContentResponse = mailchimpFunctions.addContent(campaign_id, "<body><h1>Your payment is successful</h1><p>Your payment " + paymentID + " at " + paymentDateTime + " of $" + paymentAmount + " is successful</p><p>You can now attend the tuition class.</p></body>")
                    print(addContentStatus)
                    print(addContentResponse)
                    #checklist
                    if addContentStatus == 200:
                        print("checking email")
                        response = mailchimpFunctions.checkStatus(campaign_id)
                        print(response)
                        checklistStatus, checklistResponse = mailchimpFunctions.checklist(campaign_id)
                        print(checklistStatus)
                        print(checklistResponse)
                        #send msg to those in campaign
                        if checklistStatus == 200:
                            print("sending email")
                            sendEmailStatus, sendEmailResponse = mailchimpFunctions.sendEmail(campaign_id)
                            print(sendEmailStatus)
                            print(sendEmailResponse)
                            #archive contact


if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')    
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    receiveSuccessfulPayment()
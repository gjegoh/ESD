import json
import os
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
import amqp_setup

app = Flask(__name__)

# enables cross-origin resource sharing for fetch apis
CORS(app)

monitorBindingKey='*.rejectTutor'

def receiveRejectedTutor():
    amqp_setup.check_setup()
    
    queue_name = "rejectTutor"  

    # set up a consumer and start to wait for coming messages
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived an tutor rejection by " + __file__)
    processRejectTutor(body)
    print() # print a new line feed

def processRejectTutor(body):
    print("Printing the tutor rejection message:")
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
    #create contact for rejected tutors 
    if apiKeyStatus == 200:
        email = message['email']
        print("creating new contact")
        addNewStudentStatus, addNewStudentResponse = mailchimpFunctions.addContact(email)
        print(addNewStudentStatus)
        print(addNewStudentResponse)
        #add approved tutors into reject segment
        if addNewStudentStatus == 200:
            print("add rejected tutors into reject segment:")
            segment_id, createSegmentStatus, createSegmentResponse = mailchimpFunctions.addMemberIntoSegment("reject", email)
            print(createSegmentStatus)
            print(createSegmentResponse)
            print(segment_id)
            #create campaign
            if createSegmentStatus == 200:
                campaign_name = "Rejection of Tutor Application"
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
                    addContentStatus, addContentResponse = mailchimpFunctions.addContent(campaign_id, "<body><h1>We have rejected your tutor application</h1><p>Your account will now be deleted.</p></body>")
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
                            #delete segment
                            # if sendEmailStatus == 200:
                            #     print("deleting segment")
                            #     deleteSegmentStatus, deleteSegmentResponse = mailchimpFunctions.deleteSegment(segment_id)
                            #     print(deleteSegmentStatus)
                            #     print(deleteSegmentResponse)
                            #     #delete contact
                            # if sendEmailStatus == 200:
                            #     time.sleep(30)
                            #     print("archive tutor contact in audience")
                            #     archiveContactStatus, archiveContactResponse = mailchimpFunctions.archiveContact(email)
                            #     print(archiveContactStatus)
                            #     print(archiveContactResponse)

if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')    
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    receiveRejectedTutor()
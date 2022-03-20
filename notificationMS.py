from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
import pymysql.cursors
from mailchimp3 import MailChimp
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from urllib.parse import parse_qs
import json


app = Flask(__name__)

# enables cross-origin resource sharing for fetch apis
CORS(app)


#check whether the API key is valid
#if successful, will return {"health_status": "Everything's Chimpy!"} 
try:
  client = MailchimpMarketing.Client()
  client.set_config({
    "api_key": "ccd8ccd2e76121c4fb60f120e9b6e643-us14",
    "server": "us14"
  })

  response = client.ping.get()
  print(response)
except ApiClientError as error:
  print("Error: {}".format(error.text))

#Then, we can use the API key
mailchimp = MailchimpMarketing.Client()
mailchimp.set_config({
  "api_key": "ccd8ccd2e76121c4fb60f120e9b6e643-us14",
  "server": "us14"
})

#########################################################
# https://mailchimp.com/developer/marketing/guides/create-your-first-audience/
# A contact is an individual name and email address (amongst other information)
# Audiences are lists of contacts to which you send campaigns
# The Audience/Lists endpoint lets you create and manage your audiences. 
# The Members endpoint lets you manage the contacts in those lists—creating, updating, deleting, and archiving—so you can integrate your users with your Mailchimp account.
# In Mailchimp, a contact only exists in the context of the audience it’s a member of. 
# You can’t create a contact and then later add that contact to a list—which means contacts can’t be explicitly shared between more than one list.
#You can:
#1. Create a new audience in response to events happening in your application
#2. Update contacts based on changes in your application
#3. Sync contacts from Mailchimp to your application
#########################################################

#step 1: create a audience (in reponse to a event of new class schedules being created)
#tutorMS must call notificationMS to start off step 1
@app.route("/createAudience")
def createAudience():
    body = {
      "permission_reminder": "You signed up for updates on our website",
      "email_type_option": False,
      "campaign_defaults": {
        "from_name": "tuitioncentre",
        "from_email": "tuitioncentre@mailchimp.com",
        "subject": "New Class Schedule",
        "language": "EN_US"
      },
      "name": "New Class Schedule",
      "contact": {
        "company": "tuitioncentre",
        "address1": "81 Victoria Street",
        "address2": "",
        "city": "singapore",
        "state": "",
        "zip": "188065",
        "country": "singapore"
      }
    }

    try:
      response = mailchimp.lists.create_list(body)
      return "Response: {}".format(response)
    except ApiClientError as error:
      return "An exception occurred: {}".format(error.text)

#step 2: add contacts into audiences from tutor database using batch operation request -> instead of making many api calls, we can use a single call to add all the tutors into contacts.
@app.route("/addContacts")
def addContacts():
    list_id = "1"
    
    #a. get all tutor information from database
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            # accesses tutorDB to retrieve all tutor's details
            sql = "USE tutorDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT firstName, lastName, email, phoneNumber, eduLevel, taughtSubjects, execSummary FROM tutor WHERE isApproved=1"
            cursor.execute(sql)
            tutorList = cursor.fetchall()
    
    operations = []
    #b. reiterate through all tutors
    for tutor in tutorList:
    #c. add tutor as contact
      operation = {
        "method": "POST",
        "path": f"/lists/{list_id}/members",
        "body": json.dumps({
            "email_address": tutor['email'],
            "status": "subscribed"
          })
      }
      operations.append(operation)

      payload = {
          "operations": operations
      }
      try:
        response = mailchimp.batches.start(payload)
        return "Response: {}".format(response)
      except ApiClientError as error:
        return "An exception occurred: {}".format(error.text)

#step 3: use a webhook to update the application UI that batch request to add all tutor into contacts is completed
@app.route("/setUpWebhook")
def setUpWebhook():
    #a. webhook_url must be a valid website url
    # mailchimp will send a GET request to url to ensure validity
    webhook_url = "YOUR_WEBHOOK_ABSOLUTE_URL"
    payload = {
        "url": webhook_url
    }
    try:
      response = mailchimp.batchWebhooks.create(payload)
      return "Response: {}".format(response)
    except ApiClientError as error:
      return "An exception occurred: {}".format(error.text)



#step 4: mailchimp will send info about completed batch operations, in an encoded text
#we can decode the text to get the info
@app.route("/handleWebhook")
def handleWebhook(response_body):
    response_body_url = parse_qs(response_body)
    decoded_text = response_body_url['data[response_body_url]']
    return "You can fetch the gzipped response with" + decoded_text

#step 5: send campaign emails to the contacts in the audience (informing them of new class schedule created)
@app.route("/sendCampaignEmails")
def sendCampaignEmails():
      campaignEmail = {
                        "type": "regular", 
                        "recipents": {
                          "list_id": "1"
                        }
                      }
      try:
        response = client.campaigns.create(campaignEmail)
        return "Response: {}".format(response)
      except ApiClientError as error:
        return "An exception occurred: {}".format(error.text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

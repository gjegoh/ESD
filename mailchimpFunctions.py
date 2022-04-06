from re import L
from venv import create
from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
import pymysql.cursors
from mailchimp3 import MailChimp
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from urllib.parse import parse_qs
import json
import hashlib
############################
# check how to test if email is sent properly/received etc
############################

app = Flask(__name__)

# enables cross-origin resource sharing for fetch apis
CORS(app)


#check whether the API key is valid
#if successful, will return {"health_status": "Everything's Chimpy!"} 
try:
  client = MailchimpMarketing.Client()
  client.set_config({
    "api_key": "da0da6b72eff90471e10518dd42e8926",
    "server": "us14"
  })

  response = client.ping.get()
  print(response)
except ApiClientError as error:
  print("Error: {}".format(error.text))

#Then, we can use the API key
mailchimp = MailchimpMarketing.Client()
mailchimp.set_config({
  "api_key": "da0da6b72eff90471e10518dd42e8926",
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
#3. Sync contacts from Mailchimp to your applicatio

#set up AMQP first
#see what routing key to use for registation + what should be included in the message
#  -> maybe can include params to call a certain function -> like to send account creation email


@app.route('/checkIfMember')
def checkIfMember(email):
    list_id = "d61191e75f"
    subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
    try:
      status = 200
      response = client.lists.get_list_member(list_id, subscriber_hash)
      return status, response
    except ApiClientError as error:
      status = 400
      return status, error.text

@app.route('/addContact', methods=['POST'])
def addContact(email):

    list_id = "d61191e75f"
    try:
      status = 200
      response = client.lists.add_list_member(list_id, 
                                              {
                                              "email_address": email, 
                                              "status": "subscribed"
                                              }
                                              )
      return status, response
    except ApiClientError as error:
      status = 400
      return status, error.text

    
# @app.route('/createSegment', methods=['POST'])
# def createSegment(name, email):
#     list_id = "d61191e75f"
#     try:
#       status = 200
#       response = client.lists.create_segment(list_id, {"name": name, "static_segment": [email]})
#       segment_id = response['id']
#       return segment_id, status, response
#     except ApiClientError as error:
#       status = 400
#       segment_id = "nil"
#       return segment_id, status, error.text

@app.route("/checkIfMemberInSegment")
def checkIfMemberInSegment(segmentName, email):
      list_id = "d61191e75f"
      subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
      response = client.lists.get_list_member_tags(list_id, subscriber_hash)
      segments = response['tags']
      for segment in segments:
          name = segment['name']
          if name == segmentName:
              status = 200
              return status
      status = 400
      return status
      

@app.route('/addMemberIntoSegment', methods=['POST'])
def addMemberIntoSegment(segmentName, email):
      list_id = "d61191e75f"
      payment_segment_id = 7251951
      approve_segment_id = 7251955
      reject_segment_id = 7251959
      if segmentName == "reject":
          segment_id = reject_segment_id
      if segmentName == "approve":
          segment_id = approve_segment_id
      if segmentName == "payment":
            segment_id = payment_segment_id
      try:
        status = 200
        response = client.lists.create_segment_member(list_id, segment_id, {"email_address": email})
        return segment_id, status, response
      except ApiClientError as error:
        status = 400
        segment_id = "nil"
        return segment_id, status, error.text

@app.route("/deleteTag", methods=['DELETE'])
def deleteTag(segmentName, email):
      list_id = "d61191e75f"
      subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
      try:
        status = 200
        response = client.lists.update_list_member_tags(list_id, subscriber_hash, {"tags": [{"name": segmentName, "status": "inactive"}]})
        return status, response
      except ApiClientError as error:
        status = 400
        return status, error.text  

@app.route('/createCampaign', methods=['POST'])
def createCampaign(campaign_name,from_name,reply_to, segment_id):
      list_id = "d61191e75f"
      segment_id = int(segment_id)
      CampaignDetails = {
                        "settings":
                          {
                          "subject_line": campaign_name,
                          "from_name": from_name,
                          "reply_to": reply_to
                          },
                        "type": "regular", 
                        "recipients": {
                          "list_id": list_id,
                          "segment_opts": {
                            "saved_segment_id": segment_id
                            # "match": "all",
                            # "condiitons": [{
                            #   "condition_type": "StaticSegment",
                            #   "field": "static_segment",
                            #   "op": "static_is",
                            #   "value": segment_id
                            # }]
                          }
                          } 
                      }
      try:
        status = 200
        response = client.campaigns.create(CampaignDetails)
        campaign_id = response['id']
        return campaign_id, status, response
      except ApiClientError as error:
        status = 400
        campaign_id = "nil"
        return campaign_id, status, error.text

@app.route("/addContent", methods=['POST'])
def addContent(campaign_id, html_code):
      try:
        status = 200
        response = client.campaigns.set_content(campaign_id, {"html": html_code})
        return status, response
      except ApiClientError as error:
        status = 400
        return status, error.text

@app.route("/sendTestEmail", methods=['POST'])
def sendTestEmail(campaign_id):
    try:
      status = 200
      response = client.campaigns.send_test_email(campaign_id, {"test_emails": ["jenniferwxe@gmail.com"], "send_type": "plaintext"})
      return status, response
    except ApiClientError as error:
      status = 400
      return status, error.text

@app.route("/checkStatus")
def checkStatus(campaign_id):
      try:
        status = 200
        response = client.campaigns.get(campaign_id)
        return response
      except ApiClientError as error:
        print("Error: {}".format(error.text))

@app.route("/checklist")
def checklist(campaign_id):
      try:
        status = 200
        response = client.campaigns.get_send_checklist(campaign_id)
        return status, response
      except ApiClientError as error:
        status = 400
        return status, error.text



@app.route("/sendEmail", methods=['POST'])
def sendEmail(campaign_id):
      campaign_id = str(campaign_id)
      try:
        status = 200
        response = client.campaigns.send(campaign_id)
        return status, response
      except ApiClientError as error:
        status = 400
        return status, error.text
    

# @app.route('/deleteSegment', methods=['DELETE'])
# def deleteSegment(segment_id):
#     list_id = "d61191e75f"
#     try:
#       status = 200
#       response = client.lists.delete_segment(list_id, segment_id)
#       return status, response
#     except ApiClientError as error:
#       status = 400
#       return status, error.text

# @app.route('/deleteContact', methods=['DELETE'])
# def deleteContact(email):
#       list_id = "d61191e75f"
#       subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
#       try:
#         status = 200
#         response = client.lists.delete_list_member_permanent(list_id, subscriber_hash)
#         return status, response
#       except ApiClientError as error:
#         status = 400
#         return status, error.text

@app.route('/archiveContact', methods=['DELETE'])
def archiveContact(email):
      list_id = "d61191e75f"
      subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
      try:
        status = 200
        response = client.lists.delete_list_member(list_id, subscriber_hash)
        return status, response
      except ApiClientError as error:
        status = 400
        return status, error.text

################################################
#for permenant tutors
################################################
@app.route("/addTutorTag", methods=['POST'])
def addTutorTag(email):
      # tutorTag = 509151
      list_id = list_id = "d61191e75f"
      name = "tutor"
      subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
      try:
        status = 200
        response = client.lists.update_list_member_tags(list_id, subscriber_hash, {"tags": [{"name": name, "status": "active"}]})
        return status, response
      except ApiClientError as error:
        status = 400
        return status, error.text


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)


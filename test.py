import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
import hashlib

email = "studenttuitioncentre1@gmail.com"
list_id = "d61191e75f"
subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
try:
  client = MailchimpMarketing.Client()
  client.set_config({
    "api_key": "da0da6b72eff90471e10518dd42e8926",
    "server": "us14"
  })

  response = client.lists.get_list_member(list_id, subscriber_hash)
  print(response)
except ApiClientError as error:
  print("Error: {}".format(error.text))
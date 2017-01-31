import os
import time
import json
from slackclient import SlackClient
import shutil
import requests
from clarifai import rest
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
import unirest
# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def list_channels():
    channels_call = slack_client.api_call("channels.list")
    if channels_call['ok']:
        print channels_call['channels']
        return channels_call['channels']
    return None


def channel_info(channel_id):
    channel_info = slack_client.api_call("channels.info", channel=channel_id)
    if channel_info:
        return channel_info['channel']
    return None

def send_message(channel_id, message):
    slack_client.api_call(
        "chat.postMessage",
        channel=channel_id,
        text=message,
        username='pythonbot',
        icon_emoji=':rojbot_face:'
    )

def read_file(file_id):
   slack_client.api_call(
       "files.info",
       file=file_id,
       token='xoxp-128968699074-129647659430-130721698532-39f199c8591c8dcebd0a203adf0b1a96',
       count=1,
       page=1
    )


def File(url):
    token = 'xoxp-128968699074-129647659430-130721698532-39f199c8591c8dcebd0a203adf0b1a96'
    response = requests.get(url, stream=True,headers={'Authorization': 'Bearer %s' % token})
    if response.status_code==200:
       print 200
       with open('a.jpg', 'wb') as f:
        shutil.copyfileobj(response.raw,f)
       app = ClarifaiApp("vRFXZQ1VC4WEBnurtH1XiehfUL7DgZoV4oMHcX7n", "DFzeuPqmt0T3UoMODZiCX904IV84SYOHXz0gkdTO")
       model = app.models.get('food-items-v1.0')
       image=app.inputs.create_image_from_filename("/home/aashay/a.jpg")
       a=model.predict([image])
       for i in a['outputs'][0]['data']['concepts']:
           print i['name']
           j=i['name']
           r = unirest.get("https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/findByIngredients?ingredients="+j+"&number=2&ranking=1",
              headers={
           "X-Mashape-Key": "6FqK3rSNW1mshw87nHsd9cXFsuXUp1TjKIvjsnkWYXlmgbVO41",
           "Accept": "application/json"
           }
           )

           print r.body
           
           break
    del response



if slack_client.rtm_connect():  # connect to a Slack RTM websocket
    while True:
        a= slack_client.rtm_read()
        if a:
            if (a[0]['type']=='message'):
                    if ('uploaded a file:' in (a[0]['text'])):
                        b=a[0]['file']['url_private']
                        File(b)


        time.sleep(1)
else:
    print 'Connection Failed, invalid token?'

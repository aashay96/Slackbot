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
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
# starterbot's ID as an environment variable

BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def image_predictions():
       app = ClarifaiApp("vRFXZQ1VC4WEBnurtH1XiehfUL7DgZoV4oMHcX7n", "DFzeuPqmt0T3UoMODZiCX904IV84SYOHXz0gkdTO")
       model = app.models.get('food-items-v1.0')
       image=app.inputs.create_image_from_filename("/home/aashay/a.jpg")
       predictions=model.predict([image])
       return predictions


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
        username='aashaybot',
        icon_emoji=':rojbot_face:'
    )

def read_file(file_id):
   slack_client.api_call(
       "files.info",
       file=file_id,
       token='',
       count=1,
       page=1
    )


def File(url):
    token = ''
    response = requests.get(url, stream=True,headers={'Authorization': 'Bearer %s' % token})
    if response.status_code==200:
       print 200
       with open('a.jpg', 'wb') as f:
        shutil.copyfileobj(response.raw,f)
        a = image_predictions()
        print "###########################"
        j=""
        k=0
        for i in a['outputs'][0]['data']['concepts']:
            if j=="":
                j=i['name']
                k=k+1
            else:
                j=j+"+"+i['name']
                k=k+1
            if k>4:
                break;
        print j

        r1 = unirest.get("https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/queries/analyze?q="+j,
                    headers={
        "X-Mashape-Key": "",
        "Accept": "application/json"
                            }
                            )
        j=""
        for i in r1.body['ingredients']:
            if j=="":
                j=i['name']
            else:
                j=i['name']+"\%2C"+j
        print j


        r = unirest.get("https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/findByIngredients?ingredients="+j+"&number=3&ranking=1",
              headers={
           "X-Mashape-Key": "",
           "Accept": "application/json"
           }
           )

        recipe= np.empty((0),dtype='int32')
        recipe_id=np.empty((0),dtype='int32')

        print r.body
        for i in r.body:
            recipe=np.append(recipe,i['title'])
            recipe_id=np.append(recipe_id,i['id'])
        print recipe
        print recipe_id


        for i in np.nditer(recipe_id):
            print i
            query = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/"+str(i)+"/analyzedInstructions?stepBreakdown=true"
            recipe_json = unirest.get(query,
                                headers={
            "X-Mashape-Key": "",
            "Accept": "application/json"
                }
                )
            recipe_steps = recipe_json.body
            if recipe_steps and recipe_steps[0]['steps']:
                  instruct_recipe = ""
                  for i, r_step in enumerate(recipe_steps[0]['steps']):
                    equip_str = ""
                    for e in r_step['equipment']:
                      equip_str += e['name'] + ", "
                    if not equip_str:
                      equip_str = "None"
                    else:
                      equip_str = equip_str[:-2]

                    instruct_recipe += "*Step " + str(i+1) + "*:\n" +\
                      "_Equipment_: " + equip_str + "\n" +\
                      "_Action_: " + r_step['step'] + "\n\n"
            else:
                   instruct_recipe += "_No instructions available for this recipe._\n\n"
            print instruct_recipe

    del response



if slack_client.rtm_connect():
    Message = "Hi! I am chefBot. have some left over food or ingredient and don't know what to do with them? Don't worry. I am here to help. Just send me a photo of those things and I will send you an insanely great recipe, I promise."

     # connect to a Slack RTM websocket. this module helps in downloading the file. gets the url of the file.
    while True:
        a= slack_client.rtm_read()
        if a:
            if (a[0]['type']=='message'):
                if(a[0]['text']=='Hi'):
                    send_message('C3S7PP03A',Message)
                elif ('uploaded a file:' in (a[0]['text'])):
                    b=a[0]['file']['url_private']
                    File(b)


        time.sleep(1)
else:
    print 'Connection Failed, invalid token?'

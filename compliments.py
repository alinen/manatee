from keys import consumer_key, consumer_secret, access_token_key, access_token_secret

import json, sys, requests, os
from requests_oauthlib import OAuth1Session

import random, time, string, os
import base64
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

def drawMessage(img, x, y, msg):
    strokec = (0,0,0,255)
    fillc = (255,255,255,255)
    font = ImageFont.truetype("Impact.ttf", 42)
    draw = ImageDraw.Draw(img)
    draw.text((x-1, y-1), msg, font=font, fill=strokec)
    draw.text((x+1, y-1), msg, font=font, fill=strokec)
    draw.text((x-1, y+1), msg, font=font, fill=strokec)
    draw.text((x+1, y+1), msg, font=font, fill=strokec)
    draw.text((x, y), msg, font=font, fill=fillc)

def getCurrent():
    if os.path.isfile("current.txt"):
       f = open("current.txt", "r")
       lines = f.readlines()
       current = int(lines[0])
       f.close()
       return current
    return 0

def setNext(nextIdx):
    f = open("current.txt", "w")
    f.writelines("%d\n"%nextIdx)
    f.close()

def generateComplimentOrder(numCompliments):
    values = range(0,numCompliments)
    random.shuffle(values)
    f = open("order.txt", "w")
    for v in values:
       f.writelines("%d\n"%v)
    f.close()

def getComplimentId(current, numCompliments):
    if not os.path.isfile("order.txt"):
       generateComplimentOrder(numCompliments)

    print current, numCompliments
    f = open("order.txt", "r")
    valueStrings = f.readlines()
    v = int(valueStrings[current])
    f.close()
    return v

def createImage():
    random.seed(time.time())

    # open message
    f = open("compliments.txt", "r")
    compliments = f.readlines()
    numCompliments = len(compliments)
    f.close()

    # open random image
    files = os.listdir("pics")
    names = [f for f in files if ".jpg" in f]
    idx = random.randint(0, len(names)-1)
    name = names[idx]

    # get manatee state
    current = getCurrent()
    if current > numCompliments-1:
       generateComplimentOrder(numCompliments)
       current = 0
    idx = getComplimentId(current, numCompliments)
    setNext(current+1)

    message = string.strip(compliments[idx])

    print name
    print message
    img = Image.open("pics/"+name)
    maxCharsPerLine = 40
    if len(message) > maxCharsPerLine:
       i = maxCharsPerLine
       c = message[i-1]
       while message[i] != ' ':
          i = i - 1
       message1 = message[0:i]
       message2 = message[i+1:-1]
       drawMessage(img, 10,400, message1)
       drawMessage(img, 10,450, message2)
    else:
       drawMessage(img, 10,450, message)
    img.save('test.jpg')

def tweet():
    with open("test.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    
    twitter = OAuth1Session(consumer_key,
                            client_secret = consumer_secret,
                            resource_owner_key = access_token_key,
                            resource_owner_secret = access_token_secret)
    
    url="https://upload.twitter.com/1.1/media/upload.json"
    r = twitter.post(url, files={"media_data":encoded_string})
    tmp = json.loads(r.content)
    media_id = tmp["media_id"]
    print media_id
    
    url="https://api.twitter.com/1.1/statuses/update.json"
    r = twitter.post(url, data={"status": "thinking of you #manatee", "media_ids": [media_id]})
    print r

createImage()
tweet()



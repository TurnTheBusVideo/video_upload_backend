#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 11:02:38 2020

@author: vikram
"""

import boto3

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir
import json

# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session()
polly = session.client("polly")

s3_client = boto3.client('s3')

speed = '100'

intext = 'मेरा नाम विक्रम है और मैं अदिति की आवाज़ में बोल रहा हूँ। मैं टर्न the बस के लिए काम कर रहां हूँ। '
desired_time_in_ms = 5000


##create the SSML string
text = '<speak>'+'<prosody rate="'+speed+'%">'+intext+ '<mark name="ttb"/>' + '</prosody>'+'</speak>'

response = polly.synthesize_speech(
        Text= text, 
        OutputFormat="json",
        Engine = 'standard',
        VoiceId="Aditi",
        LanguageCode = 'hi-IN',
        TextType = 'ssml',
        SpeechMarkTypes=("sentence","ssml")
       )

##find the time it takes to render it at speed 100
stream = response["AudioStream"].read().decode()
t1 = stream.replace('\n',',')
t2 = '[' + t1[:-1] + ']'
t2 = json.loads(t2)
actual_time = t2[-1]['time']

##calculate how much we will need to speed it by -- we can use int or round
speed = str(int(100*actual_time/desired_time_in_ms))

#now plug in the new speed
text = '<speak>'+'<prosody rate="'+speed+'%">'+intext+ '<mark name="ttb"/>' + '</prosody>'+'</speak>'

#get the length again
response = polly.synthesize_speech(
        Text= text, 
        OutputFormat="json",
        Engine = 'standard',
        VoiceId="Aditi",
        LanguageCode = 'hi-IN',
        TextType = 'ssml',
        SpeechMarkTypes=("sentence","ssml")
       )

stream = response["AudioStream"].read().decode()
t1 = stream.replace('\n',',')
t2 = '[' + t1[:-1] + ']'
t2 = json.loads(t2)
actual_time = t2[-1]['time']


##now generate the speech using the new speed
response = polly.synthesize_speech(
        Text= text, 
        OutputFormat="mp3",
        Engine = 'standard',
        VoiceId="Aditi",
        LanguageCode = 'hi-IN',
        TextType = 'ssml',
       )

# Access the audio stream from the response
if "AudioStream" in response:
    # Note: Closing the stream is important because the service throttles on the
    # number of parallel connections. Here we are using contextlib.closing to
    # ensure the close method of the stream object will be called automatically
    # at the end of the with statement's scope.
    with closing(response["AudioStream"]) as stream:
        #output = os.path.join(gettempdir(), "speech.mp3")
        output = "/users/vikram/downloads/speech.mp3"

        try:
            # Open a file for writing the output as a binary stream
            with open(output, "wb") as file:
                file.write(stream.read())
        except IOError as error:
            # Could not write to file, exit gracefully
            print(error)
            sys.exit(-1)

else:
    # The response didn't contain audio data, exit gracefully
    print("Could not stream audio")
    sys.exit(-1)


audio = AudioSegment.from_file('/users/vikram/Downloads/test.mp3', "mp3")
print(len(audio))

# Play the audio using the platform's default player
if sys.platform == "win32":
    os.startfile(output)
else:
    # The following works on macOS and Linux. (Darwin = mac, xdg-open = linux).
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, output])  



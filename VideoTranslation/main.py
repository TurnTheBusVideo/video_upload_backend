import boto3
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir
import json

# FFMPEG command
#ffmpeg -f concat -i audiofiles.txt -c copy output.mp3
# audio
#ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono:sample_rate=22050 -t <seconds> -q:a 9 -acodec libmp3lame out.mp3
#ffmpeg -i "Vectors what even are they.mp4" -i output.mp3 -c:v copy -map 0:v:0 -map 1:a:0 new_video.mp4
session = Session()
polly = session.client("polly")
# adding comment
def speech_generation(content,duration_ms,filename):
    speed = '100'
    intext = content
    desired_time_in_ms = duration_ms

    #text = '<speak>'+'<prosody rate="'+speed+'%">'+intext+ '<mark name="ttb"/>' + '</prosody>'+'</speak>'
    text = '<speak>'+'<prosody rate="'+speed+'%">'+intext+ '<mark name="ttb"/>' + '</prosody>'+'</speak>'
    response = polly.synthesize_speech(
            Text= text, 
            OutputFormat="json", #json
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
    """ 
    ##calculate how much we will need to speed it by -- we can use int or round
    speed = str(int(100*actual_time/desired_time_in_ms))

    #now plug in the new speed
    text = '<speak>'+'<prosody rate="'+speed+'%">'+intext+ '<mark name="ttb"/>' + '</prosody>'+'</speak>'
    """
    response = polly.synthesize_speech(
        Text= text, 
        OutputFormat="mp3",
        Engine = 'standard',
        VoiceId="Aditi",
        LanguageCode = 'hi-IN',
        TextType = 'ssml',
       ) 
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
            #output = os.path.join(gettempdir(), "speech.mp3")
            output = "/Users/annsarapaul/GitHub/TTB:video_upload_backend/Sample Video/" + filename

            try:
                # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
                return(actual_time)
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)



translate = boto3.client(service_name='translate', region_name='ap-south-1', use_ssl=True)
"""
result = translate.translate_text(Text="Hello, World", 
            SourceLanguageCode="en", TargetLanguageCode="hi")
print('TranslatedText: ' + result.get('TranslatedText'))
print('SourceLanguageCode: ' + result.get('SourceLanguageCode'))
print('TargetLanguageCode: ' + result.get('TargetLanguageCode'))
"""

with open('/Users/annsarapaul/GitHub/TTB:video_upload_backend/Sample Video/transcribe.json') as f:
  data = json.load(f)

phrases = []
phrase = {}
for item in data['results']['items']:
    if (len(phrase) == 0) & (item['type'] == 'pronunciation'):
        phrase['word'] = item['alternatives'][0]['content']
        phrase['start_time'] = item['start_time']
        phrase['end_time'] = item['end_time']
    elif (item['type'] == 'pronunciation'):
        phrase['word'] = phrase['word'] + ' ' + item['alternatives'][0]['content']
        phrase['end_time'] = item['end_time']        
    elif (len(phrase) != 0) & (item['alternatives'][0]['content'] == '.'):
        #End of Phrase
        phrases.append(phrase)
        phrase = {}
    elif (len(phrase) != 0):
        phrase['word'] = phrase['word'] + ' ' + item['alternatives'][0]['content']

i = 1
for phrase in phrases:
    phrase['duration'] = (float(phrase['end_time']) - float(phrase['start_time']))*1000
    result = translate.translate_text(Text=phrase['word'], SourceLanguageCode="en", TargetLanguageCode="hi")
    phrase['translation'] = result.get('TranslatedText')
    phrase['audiofile'] = 'speech_' + str(i).zfill(4) + ".mp3"
    phrase['actual_time'] = speech_generation(phrase['translation'],phrase['duration'],phrase['audiofile'])
    i = i +1
with open('/Users/annsarapaul/GitHub/TTB:video_upload_backend/Sample Video/translate_output.json', 'w',encoding='utf8') as outfile:
    json.dump(phrases, outfile, ensure_ascii=False)





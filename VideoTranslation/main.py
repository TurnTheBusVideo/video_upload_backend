import boto3
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir
import json

translate = boto3.client(service_name='translate', region_name='ap-south-1', use_ssl=True)

result = translate.translate_text(Text="Hello, World", 
            SourceLanguageCode="en", TargetLanguageCode="hi")
print('TranslatedText: ' + result.get('TranslatedText'))
print('SourceLanguageCode: ' + result.get('SourceLanguageCode'))
print('TargetLanguageCode: ' + result.get('TargetLanguageCode'))


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
    elif (len(phrase) != 0):
        #End of Phrase
        phrases.append(phrase)
        phrase = {}

for phrase in phrases:
    phrase['duration'] = (phrase['end_time'] - phrase['start_time'])*1000
    result = translate.translate_text(Text=phrase['word'], SourceLanguageCode="en", TargetLanguageCode="hi")
    phrase['translation'] = result.get('TranslatedText')

with open('/Users/annsarapaul/GitHub/TTB:video_upload_backend/Sample Video/translate_output.json', 'w',encoding='utf8') as outfile:
    json.dump(phrases, outfile, ensure_ascii=False)





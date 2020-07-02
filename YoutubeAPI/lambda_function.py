# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.insert
# NOTES:
# 1. This sample code uploads a file and can't be executed via this interface.
#    To test this code, you must run it locally using your own API credentials.
#    See: https://developers.google.com/explorer-help/guides/code_samples#python
# 2. This example makes a simple upload request. We recommend that you consider
#    using resumable uploads instead, particularly if you are transferring large
#    files or there's a high likelihood of a network interruption or other
#    transmission failure. To learn more about resumable uploads, see:
#    https://developers.google.com/api-client-library/python/guide/media_upload

import os
import boto3
import json
import google_auth_oauthlib.flow
from googleapiclient import discovery
import pickle
import googleapiclient.errors
import logging

from botocore.exceptions import ClientError
import botocore.errorfactory

from google.oauth2 import service_account


from googleapiclient.http import MediaFileUpload

#scopes = ["https://www.googleapis.com/auth/youtube.upload"]
S3 = boto3.resource('s3')
s3_client = boto3.client('s3')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    ## Supports only mp4 Files
    #Variables
    #scopes = ["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtubepartner-channel-audit","https://www.googleapis.com/auth/youtubepartner"]
    logger.info(json.dumps(event))
    
    AWS_REGION = 'ap-south-1'
    VIDEO_CHANNEL = 'UCWuYgDOn2z66ZnUNmCTP0ig'
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table('UploadVideo')

    # assert event is not None and event['Records'] is not None
    # db_entry_type =  event['Records'][0]['eventName']
    # if db_entry_type == "INSERT":
    #     OBJECT_KEY = event['Records'][0]['dynamodb']['Keys']['uploadID']['S']
    OBJECT_KEY =  event['responsePayload']['OBJECT_KEY']

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    try:
        response = table.get_item(
            Key={
                'uploadID': OBJECT_KEY
                }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        BUCKET_NAME = item['Bucket']
        TEMP_FILE = '/tmp/Temp_S3File.mp4'
        #BUCKET_NAME = event['BUCKET_NAME'] #'test-turnthebus-upload'
        #OBJECT_KEY = event['OBJECT_KEY'] #'TestYoutube/Test_API.mp4'
    
        VIDEO_TITLE = item['chapterPart'] + '|' + item['chapterNumber'] + '|' + item['videoTitle'] + '|' + item['bookPartName'] + '|' + item['bookName'] + '|' + item['classN']#event['VIDEO_TITLE'] #'Test'
        VIDEO_DESCRIPTION = item['videoDescription']  + ' - ' + item['board'] + ' - ' + item['bookName']  + ' - ' + item['bookPartName']  + '|' + item['chapterName']  + '|' + item['chapterNumber']  + '|' + item['chapterPart']  + '|' + item['classN']  + '|' + item['tutorName']  + '|' + item['videoLanguage']  + '|' + item['videoTitle'] #event['VIDEO_DESCRIPTION'] #'Awesome' 
        TAGS = item['Tags']# event['TAGS']#["S3", "Test"]
        BOARD = item['board']
        CLASS = item['classN']
        LANGUAGE = item['videoLanguage']
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    SERVICE_ACCOUNT_FILE = "videopipeline-71f56f9de636.json"
    client_secrets_file = "client_secret_oayth_ttb.apps.googleusercontent.com.json"
    
    #credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    #delegated_credentials = credentials.with_subject('ann@turnthebus.org')

    #Add Logic to get diff channels (Diff pickle files)
    #token_pickleX, VIDEO_CHANNEL X

    YOUTUBE_CHANNEL = BOARD + CLASS + LANGUAGE
    if YOUTUBE_CHANNEL == "Specific":
        token_pickle = 'token.pickle'
        VIDEO_CHANNEL = 'UCWuYgDOn2z66ZnUNmCTP0ig'
    else:
        token_pickle = 'token_main.pickle'
        VIDEO_CHANNEL = 'UCc4rG0MP16xnAhMRJ4UWxTw'

    # Update code below to use token.pickle as a variable
    if os.path.exists(token_pickle):
        with open(token_pickle, 'rb') as token:
            delegated_credentials = pickle.load(token)
    else: 
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        #flow.redirect_uri = 'https://developers.google.com/oauthplayground'

        delegated_credentials = flow.run_console()

        with open(token_pickle, 'wb') as token:
                pickle.dump(delegated_credentials, token)

    youtube = discovery.build(
        api_service_name, api_version, credentials=delegated_credentials)
    # Code for S3
    
    if not file_in_s3(OBJECT_KEY, BUCKET_NAME):
        comment = "File %s not found" % OBJECT_KEY
        return {
            'statusCode': 404,
            'body': json.dumps(comment )
        }
    if OBJECT_KEY[-4:].lower() == ".mp4":
        s3_client.download_file(BUCKET_NAME, OBJECT_KEY, TEMP_FILE)
    # End of Code for S3
        media = MediaFileUpload(TEMP_FILE,resumable=True)
        request = youtube.videos().insert(
            part="snippet, status",
            #onBehalfOfContentOwnerChannel = "UCWuYgDOn2z66ZnUNmCTP0ig",
            #onBehalfOfContentOwner = "ann@turnthebus.org",
            #onBehalfOfContentOwner = "WuYgDOn2z66ZnUNmCTP0ig",
            #onBehalfOfContentOwner = "c4rG0MP16xnAhMRJ4UWxTw",
            #onBehalfOfContentOwnerChannel = "UCc4rG0MP16xnAhMRJ4UWxTw",
            body={
              "snippet": {
                "title": VIDEO_TITLE,
                "description": VIDEO_DESCRIPTION,
                "categoryId": "22",
                "channelId": VIDEO_CHANNEL,
                #"channelId": "UCc4rG0MP16xnAhMRJ4UWxTw",
                "tags": TAGS
              },
              "status": {
                "privacyStatus": "unlisted"
              }
            },

            #media_body=MediaFileUpload("Test_API.mp4")
            media_body = media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:

                print("Uploaded %d%%." % int(status.progress() * 100))
            #print("Upload Complete!")
            logger.info("Upload Complete for file %s!" % OBJECT_KEY)
        #print(response)
        logger.info(json.dumps(response))
        video_id = response['id']
        youtube_url = "https://www.youtube.com/watch?v=" + video_id
        #response = request.execute()
        
        try:
            response = table.update_item(
                Key={
                    'uploadID': OBJECT_KEY
                },
                UpdateExpression="set youtubeURL = :u,youtubeID = :y",
                ExpressionAttributeValues={
                    ':u': youtube_url,
                    ':y': video_id
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            logger.info("Updated Key %s in DB " % OBJECT_KEY)
        #Add code to delete File after upload
        #print(response)
        return {
            'statusCode': 200,
            'video_id': video_id,
            'youtube_url': youtube_url,
            'body': json.dumps('File ' + OBJECT_KEY + ' Uploaded')
        }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('File ' + OBJECT_KEY + ' is not in mp4')
        }

def file_in_s3(file_name, bucket_name):
    try:
        response = s3_client.get_object(Bucket= bucket_name, Key=file_name)
        return (response is not None) and ('Body' in response) and (response['Body'] is not None)

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return False
        else:
            raise e

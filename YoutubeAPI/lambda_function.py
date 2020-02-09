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
# import google_auth_oauthlib.flow
from googleapiclient import discovery
# import googleapiclient.errors

from google.oauth2 import service_account


from googleapiclient.http import MediaFileUpload

#scopes = ["https://www.googleapis.com/auth/youtube.upload"]



def lambda_handler(event, context):
    ## Supports only mp4 Files
    #Variables
    scopes = ["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtubepartner-channel-audit","https://www.googleapis.com/auth/youtubepartner"]
    BUCKET_NAME = event['BUCKET_NAME'] #'test-turnthebus-upload'
    OBJECT_KEY = event['OBJECT_KEY'] #'TestYoutube/Test_API.mp4'
    TEMP_FILE = '/tmp/Temp_S3File.mp4'
    VIDEO_TITLE = event['VIDEO_TITLE'] #'Test'
    VIDEO_DESCRIPTION = event['VIDEO_DESCRIPTION'] #'Awesome'
    VIDEO_CHANNEL = event['VIDEO_CHANNEL'] #'UCWuYgDOn2z66ZnUNmCTP0ig'
    TAGS = event['TAGS']#["S3", "Test"]

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    SERVICE_ACCOUNT_FILE = "videopipeline-71f56f9de636.json"
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    delegated_credentials = credentials.with_subject('ann@turnthebus.org')
    youtube = discovery.build(
        api_service_name, api_version, credentials=delegated_credentials)
    # Code for S3
    
    S3 = boto3.resource('s3')
    s3_client = boto3.client('s3')
    
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
                "privacyStatus": "public"
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
            print("Upload Complete!")
        print(response)
        
        #response = request.execute()
        
        #Add code to delete File after upload
        #print(response)
        return {
            'statusCode': 200,
            'video_id': response['id'],
            'body': json.dumps('File ' + OBJECT_KEY + ' Uploaded')
        }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('File ' + OBJECT_KEY + ' is not in mp4')
        }

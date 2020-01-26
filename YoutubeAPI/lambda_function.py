import json
import boto3
import os

#import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2 import service_account

from googleapiclient.http import MediaFileUpload

scopes = ["https://www.googleapis.com/auth/youtube.upload"]

def lambda_handler(event, context):
    # TODO implement
    S3 = boto3.client('s3')
    BUCKET_NAME = 'turn-the-bus-videos'
    mybucket = S3.Bucket(BUCKET_NAME)

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    #client_secrets_file = "client_secret_824525138655-6c49ppcebhlmqp9s5nfq6u2nc62p2t9q.apps.googleusercontent.com.json"
    #client_secrets_file = "client_secret_824525138655-dhps58m377m2rejan9d2rfm7cl5gejag.apps.googleusercontent.com.json"
    SERVICE_ACCOUNT_FILE = "videopipeline-71f56f9de636.json"
    # Get credentials and create an API client
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    delegated_credentials = credentials.with_subject('ann@turnthebus.org')

    # flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    #     client_secrets_file, scopes)
    # credentials = flow.run_console()
     youtube = googleapiclient.discovery.build(
         api_service_name, api_version, credentials=delegated_credentials)

    for my_bucket_object in mybucket.objects.filter(Prefix='XII+-+Political+Science/'): # FOLDER
        if my_bucket_object.key[-4:].lower() == ".mp4": #FILE EXTENSION
        request = youtube.videos().insert(
            part="snippet, status",
            body={
              "snippet": {
                "title": "Test",
                "description": "Awesome",
                "categoryId": "22",
                #"channelId": "UCc4rG0MP16xnAhMRJ4UWxTw",
                #"channelId": "UCc4rG0MP16xnAhMRJ4UWxTw",
                "onBehalfOfContentOwner" : "113851783885755510658",
                #"onBehalfOfContentOwner" : "c4rG0MP16xnAhMRJ4UWxTw",
                "onBehalfOfContentOwnerChannel" : "UCc4rG0MP16xnAhMRJ4UWxTw",
                "tags": [
                  "Test"
                ]
              },
              "status": {
                "privacyStatus": "public"
              }
            },
            #file = "Test_API.mp4",
            
            # TODO: For this request to work, you must replace "YOUR_FILE"
            #       with a pointer to the actual file you are uploading.
            #media_body=MediaFileUpload("Test_API.mp4")
            media_body=MediaFileUpload(my_bucket_object)
        )
        response = request.execute()

        print(response)

    return {
        'statusCode': 200,
        'body': json.dumps('File ' + x + ' Uploaded')
    }


    
    

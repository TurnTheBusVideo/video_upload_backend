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

# import google_auth_oauthlib.flow
from googleapiclient import discovery
# import googleapiclient.errors

from google.oauth2 import service_account


from googleapiclient.http import MediaFileUpload

#scopes = ["https://www.googleapis.com/auth/youtube.upload"]
scopes = ["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtubepartner-channel-audit","https://www.googleapis.com/auth/youtubepartner"]


def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    #client_secrets_file = "client_secret_824525138655-6c49ppcebhlmqp9s5nfq6u2nc62p2t9q.apps.googleusercontent.com.json"
    # client_secrets_file = "client_secret_824525138655-dhps58m377m2rejan9d2rfm7cl5gejag.apps.googleusercontent.com.json"
    SERVICE_ACCOUNT_FILE = "videopipeline-71f56f9de636.json"
    # Get credentials and create an API client
    # flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    #     client_secrets_file, scopes)
    # credentials = flow.run_console()

    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    delegated_credentials = credentials.with_subject('ann@turnthebus.org')

    youtube = discovery.build(
        api_service_name, api_version, credentials=delegated_credentials)

    request = youtube.videos().insert(
        part="snippet, status",
        onBehalfOfContentOwnerChannel = "UCWuYgDOn2z66ZnUNmCTP0ig",
        onBehalfOfContentOwner = "ann@turnthebus.org",
        #onBehalfOfContentOwner = "WuYgDOn2z66ZnUNmCTP0ig",
        #onBehalfOfContentOwner = "c4rG0MP16xnAhMRJ4UWxTw",
        #onBehalfOfContentOwnerChannel = "UCc4rG0MP16xnAhMRJ4UWxTw",
        body={
          "snippet": {
            "title": "Test",
            "description": "Awesome",
            "categoryId": "22",
            "channelId": "UCWuYgDOn2z66ZnUNmCTP0ig",
            #"channelId": "UCc4rG0MP16xnAhMRJ4UWxTw",
            #"onBehalfOfContentOwner" : "113851783885755510658",
            #"onBehalfOfContentOwner" : "c4rG0MP16xnAhMRJ4UWxTw",
            #"onBehalfOfContentOwnerChannel" : "UCc4rG0MP16xnAhMRJ4UWxTw",

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
        media_body=MediaFileUpload("Test_API.mp4")
    )
    response = request.execute()

    print(response)

if __name__ == "__main__":
    main()
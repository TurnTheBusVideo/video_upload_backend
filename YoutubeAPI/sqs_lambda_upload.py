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

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
AWS_REGION = 'ap-south-1'
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
SERVICE_ACCOUNT_FILE = "videopipeline-71f56f9de636.json"
CLIENT_SECRETS_FILE = "client_secret_oayth_ttb.apps.googleusercontent.com.json"

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
S3 = boto3.resource('s3')
s3_client = boto3.client('s3')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(json.dumps(event))

    if len(event['Records']) > 1:
        return {
            'statusCode': 400,
            'body': json.dumps("cannot process multiple SQS records, batch size should be set to 1")
        }

    # Process each record
    return process_record(event['Records'][0])


def process_record(record):
    payload = json.loads(record["body"])
    upload_id = payload["uploadID"]["S"]
    table = dynamodb.Table('UploadVideo')

    try:
        response = table.get_item(Key={'uploadID': upload_id})
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
        return {
            'statusCode': 404,
            'body': json.dumps(e.response['Error']['Message'])
        }

    item = clean_fields(response['Item'])
    bucket_name = item["Bucket"]

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    if not file_in_s3(upload_id, bucket_name):
        return {
            'statusCode': 404,
            'body': json.dumps("File {} not found".format(upload_id))
        }

    if is_mp4(upload_id):
        return upload_video(item=item, upload_id=upload_id)

    return {
        'statusCode': 400,
        'body': json.dumps('File ' + upload_id + ' is not in mp4')
    }


def is_mp4(upload_id):
    return len(upload_id) > 4 and upload_id[-4:].lower() == ".mp4"


def clean_fields(item):
    for k, v in item.iteritems():
        if v == 'NULL':
            item[k] = ''


def get_video_title(item):
    title = "{} CH {} {} {} {} {}".format(
        item['chapterPart'],
        item['chapterNumber'],
        item['videoTitle'],
        item['bookPartName'],
        item['bookName'],
        item['classN']
    )
    if len(title) >= 100:
        return title[:100]
    return title


def get_video_description(item):
    desc = "{} - {} - {} - {} {} {} {} {} By {} in {} {}".format(
        item['videoDescription'],
        item['board'],
        item['bookName'],
        item['bookPartName'],
        item['chapterName'],
        item['chapterNumber'],
        item['chapterPart'],
        item['classN'],
        item['tutorName'],
        item['videoLanguage'],
        item['videoTitle']
    )


def get_channel_options(item):
    options = {"token_pickle": 'token.pickle',
               "video_channel": 'UCWuYgDOn2z66ZnUNmCTP0ig'}
    youtube_channel = "{}{}{}".format(
        item['board'], item['classN'], item['videoLanguage'])
    if youtube_channel == "Specific":
        return options

    return {
        "token_pickle": 'token_main.pickle',
        "video_channel": 'UCc4rG0MP16xnAhMRJ4UWxTw'
    }


def get_youtube(options):
    if os.path.exists(options["token_pickle"]):
        with open(options["token_pickle"], 'rb') as token:
            delegated_credentials = pickle.load(token)
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)
        delegated_credentials = flow.run_console()
        with open(options["token_pickle"], 'wb') as token:
            pickle.dump(delegated_credentials, token)

    return discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=delegated_credentials)


def upload_video(item, upload_id):
    channel_options = get_channel_options(item)
    youtube = get_youtube(channel_options)
    video_channel = channel_options["video_channel"]
    video_title = get_video_title(item)
    logger.info("Video Title: " + video_title)

    video_description = get_video_description(item)
    tags = item['Tags']  # event['TAGS']#["S3", "Test"]
    temp_file = = '/tmp/Temp_S3File.mp4'
    s3_client.download_file(item["Bucket"], upload_id, temp_file)
    # End of Code for S3
    media = MediaFileUpload(temp_file, resumable=True)
    request = youtube.videos().insert(
        part="snippet, status",
        body={
            "snippet": {
                "title": video_title,
                "description": video_description,
                "categoryId": "22",
                "channelId": video_channel,
                "tags": tags
            },
            "status": {
                "privacyStatus": "unlisted"
            }
        },
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Uploaded %d%%." % int(status.progress() * 100))
        # print("Upload Complete!")
        logger.info("Upload Complete for file %s!" % upload_id)
    # print(response)
    logger.info(json.dumps(response))
    video_id = response['id']
    youtube_url = "https://www.youtube.com/watch?v=" + video_id
    # response = request.execute()

    update_dynamo(upload_id=upload_id, video_id=video_id,
                  youtube_url=youtube_url)

    # Add code to delete File after upload
    # print(response)
    return {
        'statusCode': 200,
        'video_id': video_id,
        'youtube_url': youtube_url,
        'body': json.dumps('File ' + upload_id + ' Uploaded')
    }


def update_dynamo(upload_id, video_id, youtube_url):
    try:
        response = table.update_item(
            Key={
                'uploadID': upload_id
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
        logger.info("Updated Key %s in DB " % upload_id)


def file_in_s3(file_name, bucket_name):
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        return (response is not None) and ('Body' in response) and (response['Body'] is not None)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return False
        else:
            raise e

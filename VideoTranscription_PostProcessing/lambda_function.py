import json
import boto3
import codecs
import logging
import time

from botocore.exceptions import ClientError
import botocore.errorfactory

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # TODO implement
    logger.info(json.dumps(event))
    job_status = event['detail']['TranscriptionJobStatus']
    logger.info("Job Status %s" % job_status)
    AWS_REGION = 'ap-south-1'
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table('TranscribeJob')
    
    try:
        response = table.get_item(
            Key={
                'JobName': event['detail']['TranscriptionJobName']
                }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        TRS_FILE_KEY = item['transcribeJobFile']
        SRT_FILE_KEY = item['srtFilePath']
        BUCKET_NAME = item['Bucket']
        OBJECT_KEY = item['videoFile']
    
        comment = process_file(TRS_FILE_KEY, SRT_FILE_KEY, BUCKET_NAME)
    
        srt_file_path = "https://" + BUCKET_NAME + ".s3."+ AWS_REGION + ".amazonaws.com/" + SRT_FILE_KEY
        obj_file_path = "https://" + BUCKET_NAME + ".s3."+ AWS_REGION + ".amazonaws.com/" + OBJECT_KEY
        table = dynamodb.Table('UploadVideo')
        try:
            response = table.update_item(
                Key={
                    'uploadID': OBJECT_KEY
                },
                UpdateExpression="set srtFilePath = :s",
                ExpressionAttributeValues={
                    ':s': srt_file_path
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            return {
                'statusCode': 200,
                'body': json.dumps(comment),
                'srt_file_path': srt_file_path,
                'obj_file_path' : obj_file_path,
                'OBJECT_KEY' : OBJECT_KEY,
                'Bucket' : BUCKET_NAME
            }
    
def upload_to_s3(bucket_name, file_name, content):
    assert bucket_name is not None
    assert file_name is not None
    assert content is not None

    s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=content.encode("utf-8"))
    logger.info("Successfully uploaded %s to %s " % (file_name, bucket_name))


def download_from_s3(bucket_name, file_name):
    assert bucket_name is not None
    assert file_name is not None

    response = s3_client.get_object(Bucket=bucket_name, Key=file_name)

    assert response is not None and response['Body'] is not None
    return response['Body']


def file_in_s3(file_name, bucket_name):
    try:
        response = s3_client.get_object(Bucket= bucket_name, Key=file_name)
        return (response is not None) and ('Body' in response) and (response['Body'] is not None)

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return False
        else:
            raise e


## Subtitle functionality
def generate_srt(transcript):
    phrases = generate_phrases(transcript)
    srt_content = generate_srt_from_phrases(phrases)
    return srt_content


def generate_srt_file(transcript_file_name, transcript_file_streaming_body, bucket_name):
    assert transcript_file_streaming_body is not None
    assert transcript_file_name is not None

    logger.info("generating srt file for transcript file: %s " % transcript_file_name)
    srt_content = generate_srt(transcript_file_streaming_body)

    logger.info("Successfully generated srt content for %s. Uploading to S3" % transcript_file_name)
    upload_to_s3(bucket_name, transcript_file_name, srt_content)


def generate_transcript_text(transcript_file_name, transcript_file_streaming_body,bucket_name):
    assert transcript_file_name is not None
    assert transcript_file_streaming_body is not None

    ts = json.load(transcript_file_streaming_body)

    if ts is None:
        logger.warning("could not parse json content for file: %s" % transcript_file_name)
        return

    transcript_list = ts['results']['transcripts']

    if transcript_list is None or len(transcript_list) == 0:
        logger.warning("no transcript list in json content for file: %s" % transcript_file_name)
        return

    transcript_content = transcript_list[0]['transcript']

    logger.info("Uploading transcript text content to S3 for file: %s" % transcript_file_name.replace("srt", "txt"))
    upload_to_s3(bucket_name, transcript_file_name.replace("srt", "txt"), transcript_content)


## Phrase contains start_time, end_time and the max 10 word text
def generate_phrases(transcript):
    ts = json.load(transcript)
    items = ts['results']['items']

    phrase =  {}
    phrases = []
    nPhrase = True
    puncDelimiter = False
    x = 0

    for item in items:
        # if it is a new phrase, then get the start_time of the first item
        if nPhrase == True:
            if item["type"] == "pronunciation":
                phrase["start_time"] = get_time_code(float(item["start_time"]))
                phrase["end_time"] = get_time_code(float(item["end_time"]) )
                nPhrase = False         
        else:    
            # We need to determine if this pronunciation or puncuation here
            # Punctuation doesn't contain timing information, so we'll want
            # to set the end_time to whatever the last word in the phrase is.
            # Since we are reading through each word sequentially, we'll set 
            # the end_time if it is a word
            if item["type"] == "pronunciation":
                phrase["end_time"] = get_time_code(float(item["end_time"]) )
            else:
                puncDelimiter = True

        # in either case, append the word to the phrase...
        transcript_word = item['alternatives'][0]["content"]

        if ("words" not in phrase):
            phrase["words"] = [ transcript_word ]
        else:
            phrase["words"].append(transcript_word)

        x += 1

        # now add the phrase to the phrases, generate a new phrase, etc.
        if x == 10 or puncDelimiter:
            #print c, phrase
            phrases.append(phrase)
            phrase = {}
            nPhrase = True
            puncDelimiter = False
            x = 0

    return phrases


def generate_srt_from_phrases(phrases):
    tokens = []
    c = 1

    for phrase in phrases:
        tokens.append(str(c))
        tokens.append(phrase["start_time"] + " --> " + phrase["end_time"])
        tokens.append(" ".join(phrase["words"]))
        tokens.append("\n")
        c += 1

    output = "\n".join(tokens)
    return output


def get_time_code(seconds):
# Format and return a string that contains the converted number of seconds into SRT format
    thund = int(seconds % 1 * 1000)
    tseconds = int(seconds)
    tsecs = ((float(tseconds) / 60) % 1) * 60
    tmins = int(tseconds / 60)
    return str( "%02d:%02d:%02d,%03d" % (00, tmins, int(tsecs), thund))
    
def process_file(transcript_file, srt_file, bucket_name):
    logger.info("Processing transcript file: %s" % transcript_file)
    if transcript_file.endswith("json"):
        logger.info("Downloading transcript file from S3: %s from bucket: %s" % (transcript_file, bucket_name))
        transcript_file_streaming_body = download_from_s3(bucket_name, transcript_file)

        logger.info("generating srt file for transcript file: %s " % transcript_file)
        generate_srt_file(srt_file, transcript_file_streaming_body, bucket_name)

        transcript_file_streaming_body = download_from_s3(bucket_name, transcript_file)
        logger.info("generating transcript text file: %s " % transcript_file)
        generate_transcript_text(srt_file, transcript_file_streaming_body, bucket_name)
    
    comment = "Completed Transcription of transcript File: %s" % transcript_file
    return comment
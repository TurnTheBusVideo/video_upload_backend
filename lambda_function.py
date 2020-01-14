import json
import boto3
import pytube

def lambda_handler(event, context):
    # TODO implement
    S3 = boto3.client('s3')
    BUCKET_NAME = 'turn-the-bus-videos'
    mybucket = S3.Bucket(BUCKET_NAME)
    
    for my_bucket_object in mybucket.objects.filter(Prefix='XII+-+Political+Science/'):
        if my_bucket_object.key[-4:].lower() == ".mp4":
            
            
    youtube = pytube.YouTube(video_url)
    video = youtube.streams.get_by_itag(22)
    x = video.download('/tmp/')
    SOURCE_FILENAME = x
    
    return {
        'statusCode': 200,
        'body': json.dumps('File ' + x + ' Uploaded')
    }

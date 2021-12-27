import boto3
import json
import logging
import os

queue_name = os.environ["SQS_NAME"]

sqs = boto3.resource("sqs")
sqs_queue = sqs.get_queue_by_name(QueueName=queue_name)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(json.dumps(event)) 

    for record in event['Records']:
        # We only care about new images
        if 'NewImage' in record['dynamodb']:
            image = record['dynamodb']['NewImage']
            sqs_queue.send_message(MessageBody=json.dumps(image))


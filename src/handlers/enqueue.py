import json
import logging
import os
from boto3 import client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SQS_QUEUE_URL = os.environ.get("EMBEDDINGS_QUEUE_URL")
sqs = client("sqs")


def run(event, context):
    if event:
        try:
            for record in event["Records"]:
                sqs.send_message(
                    QueueUrl=SQS_QUEUE_URL,
                    MessageBody=json.dumps(record["s3"]["object"]),
                )
        except Exception as e:
            logger.error("An error occurred")
            logger.error(e)
            raise e

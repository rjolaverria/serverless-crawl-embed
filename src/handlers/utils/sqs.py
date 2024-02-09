import json
import logging
import os
from boto3 import client


class EmbeddingsQueue:
    def __init__(self):
        self.client = client("sqs")
        self.queue_url = os.environ.get("EMBEDDINGS_QUEUE_URL")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

    def send_message(self, message: any):
        message_body = json.dumps(message) if not isinstance(message, str) else message
        try:
            self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message_body,
            )
        except Exception as e:
            logging.info(f"An error occurred while enqueuing message")
            logging.error(e)
            raise e


class CrawlQueue:
    def __init__(self):
        self.client = client("sqs")
        self.queue_url = os.environ.get("CRAWL_QUEUE_URL")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

    def send_message(self, message: any):
        message_body = json.dumps(message) if not isinstance(message, str) else message
        try:
            self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message_body,
            )
        except Exception as e:
            logging.info(f"An error occurred while enqueuing message")
            logging.error(e)
            raise e

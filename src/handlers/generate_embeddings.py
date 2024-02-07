import json
import logging

import urllib.parse
from .utils.s3 import BucketClient
from .utils.pinecone import PineconeClient
from .utils.openAI import OpenAIClient
from .utils.text import get_text_from_page, split_into_chunks

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run(event, context):
    if event:
        batch_item_failures = []
        sqs_batch_response = {}

        try:
            openAI = OpenAIClient()
            pinecone = PineconeClient()
            bucket = BucketClient()

            # process records in the batch
            for record in event["Records"]:
                body = json.loads(record["body"])

                # get the item from the bucket and split into chunks of text
                decoded_key = urllib.parse.unquote(body["key"])
                (text, source) = bucket.get_bucket_item(decoded_key)
                text = get_text_from_page(text)
                chunks = split_into_chunks(text)
                embeddings = [openAI.get_embedding(chunk) for chunk in chunks]

                # fetch and store the embeddings
                pinecone.store_embeddings(chunks, embeddings, source, decoded_key)

        except Exception as e:
            batch_item_failures.append({"itemIdentifier": record["messageId"]})
            logger.error("An error occurred")
            logger.error(e)

        sqs_batch_response["batchItemFailures"] = batch_item_failures
        return sqs_batch_response

import json
import logging
import os
from urllib import parse as urllib

from .utils.files import build_file_path, get_file_name
from .utils.openAI import OpenAIClient
from .utils.pinecone import PineconeClient
from .utils.s3 import SourcesBucket
from .utils.text import get_text_from_html, split_into_chunks

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

RAW_BUCKET_DIRECTORY = os.environ.get("RAW_BUCKET_DIRECTORY")
PROCESSED_BUCKET_DIRECTORY = os.environ.get("PROCESSED_BUCKET_DIRECTORY")

def run(event, context):
    if event:
        batch_item_failures = []
        sqs_batch_response = {}

        try:
            openAI = OpenAIClient()
            pinecone = PineconeClient()
            bucket = SourcesBucket()

            # process records in the batch
            for record in event["Records"]:
                body = json.loads(record["body"])

                # get the item from the bucket and split into chunks of text
                decoded_key = urllib.unquote(body["key"])
                (text, source) = bucket.get_bucket_item(decoded_key)
                text = get_text_from_html(text)

                # ignore tiny texts
                if len(text) < 10:
                    logger.info(f"Text too small to process. Skipping: {source}")
                    continue

                parsed = urllib.urlparse(source)
                local_domain = parsed.netloc
                url_path = parsed.path

                chunks = split_into_chunks(text)

                # save chunks in bucket
                chunk_keys: list[str] = []
                for i, chunk in enumerate(chunks):
                    file_name = get_file_name(f"{url_path}/chunk{i}")
                    chunk_key = build_file_path(
                        local_domain,
                        file_name,
                        "text/plain",
                        folder_name=PROCESSED_BUCKET_DIRECTORY,
                    )
                    bucket.store_bucket_item(chunk_key, chunk, source)
                    chunk_keys.append(chunk_key)

                # get and store embeddings
                embeddings = openAI.get_embeddings(chunks)
                pinecone.store_embeddings(
                    embeddings,
                    chunk_keys,
                    source,
                )

        except Exception as e:
            batch_item_failures.append({"itemIdentifier": record["messageId"]})
            logger.error("An error occurred")
            logger.error(e)

        sqs_batch_response["batchItemFailures"] = batch_item_failures
        return sqs_batch_response

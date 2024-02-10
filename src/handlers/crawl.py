import json
import logging
import os
import random
import requests
from time import sleep
from urllib.parse import urlparse

from .utils.files import build_file_path, get_content_type, get_file_name
from .utils.links import get_domain_hyperlinks, mark_and_enqueue_links
from .utils.s3 import SourcesBucket

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

RAW_BUCKET_DIRECTORY = os.environ.get("RAW_BUCKET_DIRECTORY")


def crawl(url: str, job_time: str):
    # Parse the URL and get the domain
    local_domain = urlparse(url).netloc

    response = requests.get(url)
    logger.info(response)

    content_type = get_content_type(response)
    url_path = urlparse(response.url).path
    file_name = get_file_name(url_path)
    file_path = build_file_path(
        local_domain, file_name, content_type, folder_name=RAW_BUCKET_DIRECTORY
    )

    bucket = SourcesBucket()

    if content_type != "text/html":
        logger.info("Saving raw file at: " + url)
        bucket.store_bucket_item(file_path, response.content, url)
    else:
        logger.info("Saving raw page at: " + url)
        bucket.store_bucket_item(file_path, response.text, url)
        logger.info("Done saving raw page")
        # Get the hyperlinks from the URL and add them to the queue
        # links = get_domain_hyperlinks(local_domain, url, response)
        # mark_and_enqueue_links(local_domain, links, job_time)


def run(event, context):
    if event:
        batch_item_failures = []
        sqs_batch_response = {}
        for record in event["Records"]:
            try:
                body = json.loads(record["body"])
                crawl(body["url"], body["job_time"])
            except Exception as e:
                batch_item_failures.append({"itemIdentifier": record["messageId"]})
                logger.error("An error occurred while crawling")
                logger.error(e)

            #  Random delay between 0 and 0.8 seconds to avoid throttling or getting blocked
            delay = round(random.uniform(0, 0.8), 1)
            sleep(delay)

        sqs_batch_response["batchItemFailures"] = batch_item_failures
        return sqs_batch_response

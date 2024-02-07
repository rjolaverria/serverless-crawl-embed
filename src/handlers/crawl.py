import logging
import random
import requests
from time import sleep
from urllib.parse import urlparse
from .utils.files import (
    get_content_type,
    get_file_name,
    save_file,
    save_raw_page,
    build_file_path,
)
from .utils.links import get_domain_hyperlinks, mark_and_enqueue_links

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def crawl(url: str):
    # Parse the URL and get the domain
    local_domain = urlparse(url).netloc

    response = requests.get(url)
    logger.info(response)

    content_type = get_content_type(response)
    file_name = get_file_name(response)
    file_path = build_file_path(local_domain, file_name, content_type)

    if content_type != "text/html":
        save_file(file_path, response)
    else:
        save_raw_page(file_path, response)
        logger.info("Done saving raw page")
        # Get the hyperlinks from the URL and add them to the queue
        # links = get_domain_hyperlinks(local_domain, url, response)
        # mark_and_enqueue_links(local_domain, links)


def run(event, context):
    if event:
        batch_item_failures = []
        sqs_batch_response = {}
        for record in event["Records"]:
            try:
                crawl(record["body"])
            except Exception as e:
                batch_item_failures.append({"itemIdentifier": record["messageId"]})
                logger.error("An error occurred while crawling")
                logger.error(e)

            #  Random delay between 0 and 0.8 seconds to avoid throttling or getting blocked
            delay = round(random.uniform(0, 0.8), 1)
            sleep(delay)

        sqs_batch_response["batchItemFailures"] = batch_item_failures
        return sqs_batch_response

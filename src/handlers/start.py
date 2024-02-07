import datetime
import logging
import os
from urllib.parse import urlparse
from .utils.links import mark_and_enqueue_links

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_URL = os.environ.get("BASE_URL")
SQS_QUEUE_URL = os.environ.get("CRAWL_QUEUE_URL")


def run(event, context):
    url = event or BASE_URL
    current_time = datetime.datetime.now().time()

    local_domain = urlparse(url).netloc
    mark_and_enqueue_links(local_domain, [url])

    logger.info("Your crawl started at " + str(current_time))

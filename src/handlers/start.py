from datetime import datetime
import logging
import os
from urllib.parse import urlparse
from .utils.links import mark_and_enqueue_links

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_URL = os.environ.get("BASE_URL")

def run(event, context):
    url = event or BASE_URL
    if not url:
        raise ValueError("URL is required")

    current_time = datetime.utcnow().isoformat()

    local_domain = urlparse(url).netloc
    mark_and_enqueue_links(local_domain, [url], current_time)

    logger.info("Your crawl started at " + current_time)

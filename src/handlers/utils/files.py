import logging
import os
import requests
from boto3 import resource
from urllib.parse import urlparse
import mimetypes

SOURCES_BUCKET_NAME = os.environ.get("SOURCES_BUCKET_NAME")
RAW_BUCKET_DIRECTORY = "raw"
MAX_FILENAME_LENGTH = 240

s3 = resource("s3")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_file_name(response: requests.Response):
    path = urlparse(response.url).path
    if path.startswith("/"):
        path = path[1:]
    if path == "":
        return "index"
    return path.replace("/", "-")[:MAX_FILENAME_LENGTH]


def get_content_type(response: requests.Response):
    content_type = response.headers.get("content-type") or "text/html"
    # sometimes the content type has extra information after a semicolon like "text/html; charset=utf-8"
    return content_type.split(";")[0].strip()


def build_file_path(
    local_domain: str,
    file_name: str,
    content_type: str,
    folder_name: str = RAW_BUCKET_DIRECTORY,
):
    if mimetypes.guess_type(file_name)[0] is not None:
        extension = ""
    else:
        extension = mimetypes.guess_extension(content_type) or ".txt"
    return f"{folder_name}/{local_domain}/{file_name}{extension}"


def save_file(file_path: str, response: requests.Response):
    try:
        logger.info("Getting file from: " + response.url)
        if response.status_code != 200:
            raise Exception(f"Response status code:{response.status_code}")

        object = s3.Object(SOURCES_BUCKET_NAME, file_path)
        object.put(
            Body=response.content,
            Metadata={"source": response.url},
        )

    except requests.exceptions.RequestException as e:
        logger.error("Error retrieving file from URL:")
        logger.error(e)
        raise e
    except Exception as e:
        logger.error("An error occurred:")
        logger.error(e)
        raise e


def save_raw_page(file_path: str, response: requests.Response):
    try:
        logger.info("Getting page content from: " + response.url)

        if response.status_code != 200:
            raise Exception(f"Response status code:{response.status_code}")

        object = s3.Object(SOURCES_BUCKET_NAME, file_path)
        object.put(
            Body=response.text,
            Metadata={"source": response.url},
        )
    except requests.exceptions.RequestException as e:
        logger.error("Error retrieving page content:")
        logger.error(e)
        raise e
    except Exception as e:
        logger.error("An error occurred:")
        logger.error(e)
        raise e

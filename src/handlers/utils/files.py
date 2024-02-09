import logging
import requests
import mimetypes

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_file_name(path: str):
    if path.startswith("/"):
        path = path[1:]
    if path == "":
        return "index"
    return path


def get_content_type(response: requests.Response):
    content_type = response.headers.get("content-type") or "text/html"
    # sometimes the content type has extra information after a semicolon like "text/html; charset=utf-8"
    return content_type.split(";")[0].strip()


def build_file_path(
    local_domain: str,
    file_name: str,
    content_type: str,
    folder_name: str = "",
):
    if mimetypes.guess_type(file_name)[0] is not None:
        extension = ""
    else:
        extension = mimetypes.guess_extension(content_type) or ".txt"
    return f"{folder_name}/{local_domain}/{file_name}{extension}"

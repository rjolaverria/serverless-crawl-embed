import logging
from boto3 import client
import os


class SourcesBucket:
    def __init__(self):
        self.bucket_name = os.environ.get("SOURCES_BUCKET_NAME")
        self.client = client("s3")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

    def get_bucket_item(self, key: str) -> tuple[str, str]:
        """Get the item from the bucket by key.\n
        Returns: `(body, source_url)` tuple.
        """
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=key)
            source_url = response["Metadata"].get("source", "")
            body = response["Body"].read().decode("utf-8")

            return (
                body,
                source_url,
            )
        except Exception as e:
            self.logger.error(f"Error retrieving bucket item: {e}")
            raise e

    def store_bucket_item(self, key: str, content: bytes, source_url: str = ""):
        try:
            self.client.put_object(
                Body=content,
                Bucket=self.bucket_name,
                Key=key,
                Metadata={"source": source_url},
            )
        except Exception as e:
            self.logger.error(f"Error storing item in bucket: {e}")
            raise e

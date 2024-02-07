import logging
from boto3 import client
import os


class BucketClient:
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

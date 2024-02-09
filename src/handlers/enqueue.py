import logging

from .utils.sqs import EmbeddingsQueue

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def run(event, context):
    if event:
        try:
            queue = EmbeddingsQueue()
            for record in event["Records"]:
                queue.send_message(
                    message=record["s3"]["object"],
                )
        except Exception as e:
            logger.error("An error occurred")
            logger.error(e)
            raise e

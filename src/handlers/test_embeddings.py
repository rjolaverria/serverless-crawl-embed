import logging
from .utils.pinecone import PineconeClient
from .utils.openAI import OpenAIClient
from .utils.s3 import SourcesBucket

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


import logging
from .utils.pinecone import PineconeClient
from .utils.openAI import OpenAIClient
from .utils.s3 import SourcesBucket

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def run(event, context):
    response = {}
    try:
        openAI = OpenAIClient()
        pinecone = PineconeClient()
        bucket = SourcesBucket()
        prompt_embed = openAI.get_embedding(event)

        if prompt_embed:
            res = pinecone.get_by_cosine_similarity(embed=prompt_embed, limit=5)
            response["results"] = [
                {
                    **match,
                    "text": bucket.get_bucket_item(match["metadata"]["s3_key"])[0],
                }
                for match in res["matches"]
            ]
    except Exception as e:
        logger.error(f"Error occurred while running: {e}")
        raise e
    return response

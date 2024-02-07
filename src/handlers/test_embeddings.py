import logging
from .utils.pinecone import PineconeClient
from .utils.openAI import OpenAIClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run(event, context):
    response = {}
    try:
        openAI = OpenAIClient()
        pinecone = PineconeClient()

        promptEmbed = openAI.get_embedding(event)

        if promptEmbed:
            response = pinecone.get_by_cosine_similarity(embed=promptEmbed, limit=5)
    except Exception as e:
        logger.error(f"Error occurred while running: {e}")
        raise e
    return response

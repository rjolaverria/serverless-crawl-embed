import logging
from openai import OpenAI
import os


class OpenAIClient:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.embedding_model = (
            os.environ.get("EMBEDDING_MODEL") or "text-embedding-ada-002"
        )
        self.client = OpenAI(api_key=self.api_key)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

    def get_embedding(self, text: str):
        try:
            return (
                self.client.embeddings.create(input=text, model=self.embedding_model)
                .data[0]
                .embedding
            )
        except Exception as e:
            self.logger.info(f"Error occurred while getting embedding")
            raise e

    def get_embeddings(self, texts: list[str]):
        try:
            response = self.client.embeddings.create(
                input=texts, model=self.embedding_model
            ).data

            items = [
                item.embedding for item in sorted(response, key=lambda item: item.index)
            ]
            return items
        except Exception as e:
            self.logger.info("Error occurred while getting embedding")
            raise e

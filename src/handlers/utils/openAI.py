from openai import OpenAI
import os


class OpenAIClient:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.embedding_model = (
            os.environ.get("EMBEDDING_MODEL") or "text-embedding-ada-002"
        )
        self.client = OpenAI(api_key=self.api_key)

    def get_embedding(self, text: str):
        try:
            return (
                self.client.embeddings.create(input=text, model=self.embedding_model)
                .data[0]
                .embedding
            )
        except Exception as e:
            print(f"Error occurred while getting embedding: {e}")
            return None

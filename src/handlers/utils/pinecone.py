from pinecone import Pinecone, ServerlessSpec
import os
import logging


class PineconeClient:
    """A class to store and retrieve embeddings from a Pinecone serverless storage"""

    def __init__(self):
        self.api_key = os.environ.get("PINECONE_API_KEY")
        self.pinecone = Pinecone(api_key=self.api_key)
        self.index_name = os.environ.get("PINECONE_INDEX_NAME") or "embeddings"
        self.vector_size = os.environ.get("VECTOR_SIZE") or 1536

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # create index if it doesn't exist
        # not ideal to run on every class instantiation,
        # but it's fine for this example's testing purposes
        if self.index_name not in self.pinecone.list_indexes().names():
            # if does not exist, create index
            self.pinecone.create_index(
                name=self.index_name,
                dimension=self.vector_size,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-west-2"),
            )
        self.index = self.pinecone.Index(self.index_name)

    def store_embeddings(
        self,
        chunks: list[str],
        vectors: list[list[float]],
        source: str = "",
        s3_key: str = "",
    ):
        """Store the embedding"""
        ids = [f"{s3_key}#chunk{i}" for i in range(len(chunks))]
        meta = [
            {"source_url": source, "text": chunk, "chunk_index": i, "s3_key": s3_key}
            for i, chunk in enumerate(chunks)
        ]
        vectors = list(zip(ids, vectors, meta))
        try:
            self.index.upsert(vectors=vectors)
        except Exception as e:
            self.logger.error(f"Error storing embeddings: {e}")
            raise e

    def get_by_cosine_similarity(self, embed: list[float], limit: int = 5):
        """Gets the embeddings from the database by cosine similarity"""
        try:
            return self.index.query(
                vector=embed, top_k=2, include_metadata=True
            ).to_dict()
        except Exception as e:
            self.logger.error(f"Error retrieving embeddings: {e}")
            raise e

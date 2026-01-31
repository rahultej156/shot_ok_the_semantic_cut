from qdrant_client import QdrantClient, models
from app.core.config import settings
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class VectorDBService:
    def __init__(self):
        logger.info(f"Connecting to Qdrant at: {settings.QDRANT_URL}")
        if not settings.QDRANT_API_KEY:
             logger.warning("No Qdrant API Key provided.")

        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            check_compatibility=False
        )
        self.collection_name = settings.COLLECTION_NAME

        # Check if collection exists, if not create
        try:
            if not self.client.collection_exists(self.collection_name):
                logger.info(f"Collection {self.collection_name} not found, creating...")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=384,  # all-MiniLM-L6-v2 dimension
                        distance=models.Distance.COSINE
                    )
                )
        except Exception as e:
            logger.error(f"Failed to check/create collection. Ensure Qdrant URL is correct. Error: {e}")
            raise

    def recreate_collection(self):
        """
        Delete and recreate the collection to clear all data.
        """
        try:
            logger.info("Recreating collection...")
            self.client.delete_collection(self.collection_name)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE
                )
            )
            logger.info("Collection recreated successfully.")
        except Exception as e:
            logger.error(f"Error recreating collection: {e}")
            raise

    def add_segments(self, segments: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Add segments to the vector database.
        segments: List of dicts containing metadata and text content.
                  Must have a unique 'id' field.
        embeddings: List of embedding vectors corresponding to segments.
        """
        points = []
        for i, seg in enumerate(segments):
            # payload includes text and other metadata, excluding 'id' which is used as point id
            payload = {k: v for k, v in seg.items() if k != "id"}
            
            points.append(models.PointStruct(
                id=seg["id"],
                vector=embeddings[i],
                payload=payload
            ))

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Added {len(segments)} segments to Qdrant.")

    def search(self, query_embedding: List[float], n_results: int = 20):
        """
        Search for nearest neighbors.
        Returns a list of ScoredPoint objects.
        """
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=n_results
        )

vector_db = VectorDBService()

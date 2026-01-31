from app.core.config import settings
from sentence_transformers import SentenceTransformer, CrossEncoder
import logging

logger = logging.getLogger(__name__)

class ModelService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance._initialize_models()
        return cls._instance

    def _initialize_models(self):
        logger.info(f"Loading Embedding Model: {settings.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        logger.info(f"Loading Reranker Model: {settings.RERANKER_MODEL}")
        self.reranker_model = CrossEncoder(settings.RERANKER_MODEL)
        logger.info("Models loaded successfully.")

    def get_embedding(self, text: str):
        return self.embedding_model.encode(text).tolist()

    def rerank(self, query: str, documents: list[str]):
        """
        Reranks a list of documents based on the query.
        Returns a list of (index, score) tuples, sorted by score descending.
        """
        if not documents:
            return []
            
        pairs = [[query, doc] for doc in documents]
        scores = self.reranker_model.predict(pairs)
        
        # Combine index with score
        results = list(enumerate(scores))
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results

model_service = ModelService()

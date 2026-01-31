from app.core.config import settings
from sentence_transformers import SentenceTransformer, CrossEncoder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download():
    logger.info("Downloading Embedding Model...")
    SentenceTransformer("all-MiniLM-L6-v2")
    
    logger.info("Downloading Reranker Model...")
    CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    
    logger.info("Done!")

if __name__ == "__main__":
    download()

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

# Set cache dir to D drive to avoid space issues on C
os.environ['HF_HOME'] = "d:/Rahul/cineAI/data/hf_cache"

class Settings(BaseSettings):
    PROJECT_NAME: str = "The Semantic Cut"
    API_V1_STR: str = "/api/v1"
    
    # AI Models
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    
    # Vector DB
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    COLLECTION_NAME: str = "footage_transcripts"
    
    # Google Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-2.5-flash"

    class Config:
        case_sensitive = True

settings = Settings()

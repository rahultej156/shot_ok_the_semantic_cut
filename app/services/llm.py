import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        else:
            logger.warning("GEMINI_API_KEY not found. LLM features will be disabled.")
            self.model = None

    def generate_response(self, query: str, context: str) -> str:
        if not self.model:
            return "LLM service unavailable."
        
        prompt = f"""
        You are a helpful assistant for a video footage search engine.
        User Query: "{query}"
        
        Top matching footage segments:
        {context}
        
        Please provide a concise summary of why these clips are relevant to the user's query.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return "Error generating summary."

llm_service = LLMService()

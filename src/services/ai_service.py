"""
AI Service
Simplified OpenAI integration for generating chat responses.
"""
import logging

from openai import OpenAI
from src.utils.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE

logger = logging.getLogger(__name__)


class AIService:
    """Service class for OpenAI chat completions"""
    
    def __init__(self):
        """Initialize OpenAI client with API key from config"""
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate AI response using OpenAI chat completions.
        
        Args:
            system_prompt: System message defining AI behavior and constraints
            user_prompt: User message with context and question
            
        Returns:
            Generated response text, or fallback message on error
            
        Example:
            >>> ai = AIService()
            >>> reply = ai.generate_response(
            ...     system_prompt="You are a helpful assistant",
            ...     user_prompt="What is 2+2?"
            ... )
            >>> print(reply)
            "4"
        """
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            
            reply = response.choices[0].message.content
            return reply.strip() if reply else "Desculpe, não consegui gerar uma resposta."
            
        except Exception as e:
            logger.exception("OpenAI API call failed: %s", e)
            return "Desculpe, tive um problema ao processar sua solicitação. Tente novamente em instantes."

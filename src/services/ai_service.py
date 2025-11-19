"""
AI Service
Simplified OpenAI integration for generating chat responses.
Supports user-specific credentials instead of global configuration.
"""
import logging
from typing import Optional

from openai import OpenAI
from src.utils.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE

logger = logging.getLogger(__name__)


class AIService:
    """
    Service class for AI chat completions.
    
    Supports multiple providers (currently OpenAI).
    Uses user-specific credentials when provided, falls back to global config.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, organization_id: Optional[str] = None):
        """
        Initialize AI client with custom or default credentials.
        
        Args:
            api_key: API key for the provider (uses OPENAI_API_KEY from .env if None)
            base_url: Optional custom base URL for API
            organization_id: Optional organization ID
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.base_url = base_url
        self.organization_id = organization_id
        
        # Initialize OpenAI client with provided or default credentials
        client_kwargs = {"api_key": self.api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        if organization_id:
            client_kwargs["organization"] = organization_id
            
        self.client = OpenAI(**client_kwargs)
        logger.info(f"AIService initialized with {'custom' if api_key else 'default'} credentials")

    def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate AI response using chat completions.
        
        Args:
            system_prompt: System message defining AI behavior and constraints
            user_prompt: User message with context and question
            model: Model to use (uses OPENAI_MODEL from .env if None)
            temperature: Temperature setting 0.0-2.0 (uses OPENAI_TEMPERATURE from .env if None)
            
        Returns:
            Generated response text, or fallback message on error
            
        Example:
            >>> ai = AIService(api_key="sk-...")
            >>> reply = ai.generate_response(
            ...     system_prompt="You are a helpful assistant",
            ...     user_prompt="What is 2+2?",
            ...     model="gpt-4o-mini",
            ...     temperature=0.2
            ... )
            >>> print(reply)
            "4"
        """
        # Use provided parameters or fall back to config defaults
        model_to_use = model or OPENAI_MODEL
        temp_to_use = temperature if temperature is not None else OPENAI_TEMPERATURE
        
        try:
            response = self.client.chat.completions.create(
                model=model_to_use,
                temperature=temp_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            
            reply = response.choices[0].message.content
            logger.info(f"AI response generated successfully using model={model_to_use}")
            return reply.strip() if reply else "Desculpe, não consegui gerar uma resposta."
            
        except Exception as e:
            logger.exception("AI API call failed with model=%s: %s", model_to_use, e)
            return "Desculpe, tive um problema ao processar sua solicitação. Tente novamente em instantes."

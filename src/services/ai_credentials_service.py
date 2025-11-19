"""
AI Credentials Service
Handles fetching user-specific AI provider credentials from Supabase.
"""
import logging
from typing import Optional, Dict, Any

from src.services.supabase_service import _client
from src.utils.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE

logger = logging.getLogger(__name__)


def get_default_credentials() -> Dict[str, Any]:
    """
    Get default credentials from .env file.
    
    Returns:
        Dictionary with default credentials from environment variables
    """
    return {
        "provider": "openai",
        "api_key_encrypted": OPENAI_API_KEY,
        "default_model": OPENAI_MODEL,
        "temperature": OPENAI_TEMPERATURE,
        "base_url": None,
        "organization_id": None,
        "is_active": True
    }


def get_user_ai_credentials(user_id: str) -> Dict[str, Any]:
    """
    Fetch AI provider credentials for a specific user from ai_credentials table.
    
    This function retrieves the user's configured AI provider credentials
    (OpenAI, Anthropic, Google, etc.) to use for generating responses.
    
    Args:
        user_id: User UUID from auth.users
        
    Returns:
        Dictionary with credentials configuration:
        - provider: AI provider name (openai, anthropic, google, cohere)
        - api_key_encrypted: API key for the provider
        - default_model: Default model to use (e.g., gpt-4o-mini)
        - temperature: Temperature setting (0.0-2.0)
        - base_url: Optional custom base URL
        - organization_id: Optional organization ID
        - is_active: Whether credentials are active
        
    Example:
        >>> creds = get_user_ai_credentials("uuid-here")
        >>> print(creds["provider"])
        "openai"
        >>> print(creds["default_model"])
        "gpt-4o-mini"
    """
    try:
        # Use .maybe_single() instead of .single() to handle "no rows" gracefully
        result = _client.table("ai_credentials") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("is_active", True) \
            .maybe_single() \
            .execute()
        
        if result.data:
            logger.info(f"AI credentials found for user_id={user_id[-4:]} provider={result.data.get('provider')}")
            return result.data
        else:
            logger.warning(f"No AI credentials found for user_id={user_id[-4:]}, using defaults from .env")
            return get_default_credentials()
            
    except Exception as e:
        logger.exception(f"Failed to fetch AI credentials for user_id={user_id[-4:]}: {e}")
        return get_default_credentials()


def validate_credentials(credentials: Dict[str, Any]) -> bool:
    """
    Validate that credentials have required fields.
    
    Args:
        credentials: Credentials dictionary
        
    Returns:
        True if valid, False otherwise
    """
    if not credentials:
        return False
        
    # Check required fields
    required_fields = ["provider", "api_key_encrypted"]
    for field in required_fields:
        if not credentials.get(field):
            logger.error(f"Missing required credential field: {field}")
            return False
    
    return True


def get_temperature(credentials: Dict[str, Any], default: float = 0.2) -> float:
    """
    Extract temperature from credentials with fallback.
    
    Args:
        credentials: Credentials dictionary
        default: Default temperature if not found
        
    Returns:
        Temperature value (0.0-2.0)
    """
    try:
        temp = credentials.get("temperature")
        if temp is None:
            return default
        return float(temp)
    except (ValueError, TypeError):
        logger.warning(f"Invalid temperature value: {credentials.get('temperature')}, using default {default}")
        return default

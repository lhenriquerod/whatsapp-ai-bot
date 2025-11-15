"""
User Configuration Service
Handles fetching user-specific configurations from Supabase.
"""
import logging
from typing import Optional, Dict, Any

from src.services.supabase_service import _client

logger = logging.getLogger(__name__)


def get_user_config(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch user configuration from configuracao_empresa table.
    
    Args:
        user_id: User UUID
        
    Returns:
        Dictionary with user configuration or None if not found
        
    Example:
        >>> config = get_user_config("uuid-here")
        >>> print(config.get("tom_voz"))
        "amigavel"
    """
    try:
        result = _client.table("configuracao_empresa") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        logger.warning(f"No configuration found for user_id={user_id}")
        return None
        
    except Exception as e:
        logger.exception(f"Error fetching user config for user_id={user_id}: {e}")
        return None


def build_system_prompt(context: str, user_config: Optional[Dict[str, Any]] = None) -> str:
    """
    Build system prompt using context and user configuration.
    
    Args:
        context: Knowledge base context
        user_config: Optional user configuration from configuracao_empresa
        
    Returns:
        System prompt string
    """
    # Base prompt
    base_prompt = (
        "Você é um agente de atendimento inteligente. "
        "Responda em português, de forma precisa, breve e alinhada à marca do cliente. "
        "Use apenas o contexto fornecido. "
        "Se não souber a resposta com base no contexto, diga que não tem essa informação."
    )
    
    # If user has custom configuration, enhance the prompt
    if user_config:
        empresa = user_config.get("nome_empresa", "")
        tom_voz = user_config.get("tom_voz", "amigavel")
        prompt_persona = user_config.get("prompt_base_persona")
        
        # Use custom persona if provided
        if prompt_persona:
            base_prompt = prompt_persona
        else:
            # Enhance with company name and tone
            if empresa:
                base_prompt = f"Você é o agente de atendimento da {empresa}. " + base_prompt
            
            # Add tone guidance
            tone_guide = {
                "formal": "Mantenha um tom formal e profissional.",
                "amigavel": "Mantenha um tom amigável e acolhedor.",
                "objetivo": "Seja direto e objetivo nas respostas.",
                "descontraido": "Use um tom descontraído e informal."
            }
            
            if tom_voz in tone_guide:
                base_prompt += f" {tone_guide[tom_voz]}"
    
    return base_prompt

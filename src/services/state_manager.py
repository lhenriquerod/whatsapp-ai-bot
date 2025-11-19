"""
Conversation State Manager
Gerencia os estados da conversa para coleta de informações do usuário.
"""
import logging
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime

from src.services.supabase_service import _client

logger = logging.getLogger(__name__)


class ConversationState(str, Enum):
    """Estados possíveis de uma conversa"""
    AWAITING_NAME = "AWAITING_NAME"        # Aguardando nome do usuário
    CONFIRMING_NAME = "CONFIRMING_NAME"    # Aguardando confirmação do nome
    ACTIVE = "ACTIVE"                       # Conversa normal (nome já coletado)


# Cache temporário para nomes pendentes de confirmação
# TODO: Migrar para Redis em produção
_temp_names: Dict[str, str] = {}


def get_or_create_conversation_with_state(
    phone_number: str,
    user_id: Optional[str] = None,
    external_contact_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Busca conversa existente ou cria nova com estado apropriado.
    
    Se não existe conversa ou não tem nome, inicia com AWAITING_NAME.
    
    Args:
        phone_number: Número de telefone do contato
        user_id: ID do usuário (empresa) no sistema
        external_contact_id: ID externo do contato (mesmo que phone_number geralmente)
        
    Returns:
        Dicionário com dados da conversa
    """
    try:
        # Buscar conversa existente pelo external_contact_id ou phone_number
        search_field = external_contact_id or phone_number
        
        result = _client.table("conversations") \
            .select("*") \
            .eq("external_contact_id", search_field) \
            .execute()
        
        if result.data and len(result.data) > 0:
            conversation = result.data[0]
            
            # Se não tem nome, mudar estado para AWAITING_NAME
            if not conversation.get('contact_name'):
                logger.info(f"Conversa {conversation['id']} sem nome, mudando para AWAITING_NAME")
                update_conversation_state(conversation['id'], ConversationState.AWAITING_NAME)
                conversation['conversation_state'] = ConversationState.AWAITING_NAME
            
            return conversation
        
        # Criar nova conversa com estado AWAITING_NAME
        logger.info(f"Criando nova conversa para {search_field}")
        new_conversation = {
            'external_contact_id': search_field,
            'contact_name': None,
            'conversation_state': ConversationState.AWAITING_NAME,
            'status': 'open'
        }
        
        # Adicionar user_id apenas se fornecido
        if user_id:
            new_conversation['user_id'] = user_id
        
        result = _client.table("conversations") \
            .insert(new_conversation) \
            .execute()
        
        return result.data[0]
        
    except Exception as e:
        logger.exception(f"Erro ao buscar/criar conversa: {e}")
        raise


def update_conversation_state(conversation_id: str, new_state: ConversationState) -> None:
    """
    Atualiza o estado da conversa.
    
    Args:
        conversation_id: UUID da conversa
        new_state: Novo estado (ConversationState)
    """
    try:
        _client.table("conversations") \
            .update({
                'conversation_state': new_state.value,
                'updated_at': datetime.utcnow().isoformat()
            }) \
            .eq("id", conversation_id) \
            .execute()
        
        logger.info(f"Conversa {conversation_id} atualizada para estado {new_state}")
        
    except Exception as e:
        logger.exception(f"Erro ao atualizar estado da conversa: {e}")
        raise


def update_conversation_name(conversation_id: str, name: str) -> None:
    """
    Salva o nome do contato na conversa e muda estado para ACTIVE.
    
    Args:
        conversation_id: UUID da conversa
        name: Nome do contato
    """
    try:
        _client.table("conversations") \
            .update({
                'contact_name': name,
                'conversation_state': ConversationState.ACTIVE.value,
                'updated_at': datetime.utcnow().isoformat()
            }) \
            .eq("id", conversation_id) \
            .execute()
        
        logger.info(f"Nome '{name}' salvo para conversa {conversation_id}")
        
    except Exception as e:
        logger.exception(f"Erro ao salvar nome do contato: {e}")
        raise


def save_temp_name(conversation_id: str, name: str) -> None:
    """
    Salva nome temporariamente aguardando confirmação.
    
    Args:
        conversation_id: UUID da conversa
        name: Nome a ser confirmado
    """
    _temp_names[conversation_id] = name
    logger.debug(f"Nome temporário '{name}' salvo para conversa {conversation_id}")


def get_temp_name(conversation_id: str) -> str:
    """
    Recupera nome temporário aguardando confirmação.
    
    Args:
        conversation_id: UUID da conversa
        
    Returns:
        Nome temporário ou string vazia se não existir
    """
    return _temp_names.get(conversation_id, "")


def clear_temp_name(conversation_id: str) -> None:
    """
    Remove nome temporário do cache.
    
    Args:
        conversation_id: UUID da conversa
    """
    _temp_names.pop(conversation_id, None)
    logger.debug(f"Nome temporário removido para conversa {conversation_id}")


def get_conversation_state(conversation_id: str) -> Optional[ConversationState]:
    """
    Busca o estado atual de uma conversa.
    
    Args:
        conversation_id: UUID da conversa
        
    Returns:
        ConversationState ou None se não encontrado
    """
    try:
        result = _client.table("conversations") \
            .select("conversation_state") \
            .eq("id", conversation_id) \
            .single() \
            .execute()
        
        if result.data:
            state_value = result.data.get('conversation_state', ConversationState.ACTIVE)
            return ConversationState(state_value)
        
        return None
        
    except Exception as e:
        logger.exception(f"Erro ao buscar estado da conversa: {e}")
        return None

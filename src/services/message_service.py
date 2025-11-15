"""
Message Service
Handles message-related database operations.
"""
import logging
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from src.services.supabase_service import _client
from src.models.message import MessageCreateRequest
from src.models.conversation import ConversationUpsertRequest
from src.services import conversation_service

logger = logging.getLogger(__name__)


def get_conversation_history(
    user_id: str,
    external_contact_id: str,
    limit: int = 10
) -> tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Fetch recent message history for a conversation and contact name.
    
    Args:
        user_id: User identifier (owner of the conversation)
        external_contact_id: External contact ID (e.g., phone number)
        limit: Maximum number of messages to fetch (default: 10)
        
    Returns:
        Tuple of (messages, contact_name) where:
        - messages: List of message dictionaries ordered by timestamp (oldest first)
        - contact_name: Name of the contact from conversas table (or None)
        
    Example:
        >>> messages, name = get_conversation_history("user-123", "+5511999999999")
        >>> print(f"Conversation with {name}")
        >>> for msg in messages:
        ...     print(f"{msg['direction']}: {msg['mensagem']}")
    """
    try:
        # First, find the conversation_id and contact_name
        conv_result = _client.table("conversas") \
            .select("id, contact_name") \
            .eq("user_id", user_id) \
            .eq("external_contact_id", external_contact_id) \
            .execute()
        
        if not conv_result.data:
            logger.info(f"No conversation found for user_id={user_id[-4:]} contact={external_contact_id}")
            return [], None
        
        conversation_id = conv_result.data[0]['id']
        contact_name = conv_result.data[0].get('contact_name')
        
        # Then, fetch messages for that conversation
        result = _client.table("mensagens") \
            .select("direction, mensagem, timestamp") \
            .eq("conversa_id", conversation_id) \
            .order("timestamp", desc=False) \
            .limit(limit) \
            .execute()
        
        if result.data:
            logger.info(f"Found {len(result.data)} messages in conversation history")
            return result.data, contact_name
        
        logger.info("No conversation history found")
        return [], contact_name
        
    except Exception as e:
        logger.exception(f"Error fetching conversation history: {e}")
        return [], None


async def create_message(request: MessageCreateRequest) -> tuple[str, str]:
    """
    Create a new message record.
    
    Args:
        request: MessageCreateRequest with message data
        
    Returns:
        Tuple of (message_id, conversation_id)
        
    Raises:
        ValueError: If conversation_id is invalid
        Exception: If database operation fails
    """
    try:
        # Resolve conversation_id
        conversation_id = request.conversation_id
        
        if conversation_id:
            # Verify conversation exists
            result = _client.table("conversas") \
                .select("id") \
                .eq("id", conversation_id) \
                .execute()
            
            if not result.data or len(result.data) == 0:
                raise ValueError(f"Conversation {conversation_id} not found")
        
        else:
            # No conversation_id provided - look it up or create
            conversation_id = await conversation_service.get_conversation_by_contact(
                request.user_id,
                request.external_contact_id
            )
            
            if not conversation_id:
                # Create new conversation
                logger.info(
                    f"No conversation found for user {request.user_id} "
                    f"and contact {request.external_contact_id} - creating new"
                )
                
                upsert_request = ConversationUpsertRequest(
                    user_id=request.user_id,
                    external_contact_id=request.external_contact_id,
                    source="whatsapp",  # Default source
                    status="open"
                )
                
                conversation_id, _ = await conversation_service.upsert_conversation(upsert_request)
        
        # Prepare message data
        timestamp = None
        if request.timestamp_ts:
            timestamp = datetime.utcfromtimestamp(request.timestamp_ts).isoformat()
        
        # Mapear type para tipo (usuario/agente)
        db_tipo = {
            "user": "usuario",
            "assistant": "agente",
            "system": "agente"
        }.get(request.type, "usuario")
        
        message_data = {
            "conversa_id": conversation_id,  # Nome correto da coluna
            "tipo": db_tipo,  # Mapear para usuario/agente
            "mensagem": request.text,  # Nome correto da coluna
            "direction": request.direction,
            "external_contact_id": request.external_contact_id,
            "user_id": request.user_id,  # Adicionar user_id nas mensagens
        }
        
        if timestamp:
            message_data["timestamp"] = timestamp
        
        if request.metadata:
            # metadata já é JSONB, não precisa serializar
            message_data["metadata"] = request.metadata
        
        # Insert message na tabela mensagens
        result = _client.table("mensagens") \
            .insert(message_data) \
            .execute()
        
        if not result.data or len(result.data) == 0:
            raise Exception("Failed to create message - no data returned")
        
        message_id = result.data[0]["id"]
        
        logger.info(
            f"Created message {message_id} for conversation {conversation_id} "
            f"(direction: {request.direction}, type: {request.type})"
        )
        
        return message_id, conversation_id
        
    except ValueError:
        # Re-raise validation errors
        raise
    except Exception as e:
        logger.exception(f"Error creating message: {e}")
        raise

"""
Conversation Service
Handles conversation-related database operations.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import Client

from src.services.supabase_service import _client
from src.models.conversation import ConversationUpsertRequest

logger = logging.getLogger(__name__)


async def upsert_conversation(request: ConversationUpsertRequest) -> tuple[str, bool]:
    """
    Upsert a conversation record.
    
    Args:
        request: ConversationUpsertRequest with conversation data
        
    Returns:
        Tuple of (conversation_id, created) where created indicates if it was newly created
        
    Raises:
        Exception: If database operation fails
    """
    try:
        logger.info(f"Upserting conversation for user_id={request.user_id}, contact={request.external_contact_id}")
        
        # Check if conversation exists
        existing = _client.table("conversations") \
            .select("id, status, contact_name, title") \
            .eq("user_id", request.user_id) \
            .eq("external_contact_id", request.external_contact_id) \
            .execute()
        
        logger.debug(f"Existing conversations found: {len(existing.data) if existing.data else 0}")
        
        if existing.data and len(existing.data) > 0:
            # Conversation exists - update if needed
            conversation = existing.data[0]
            conversation_id = conversation["id"]
            
            # Prepare updates
            updates: Dict[str, Any] = {"updated_at": datetime.utcnow().isoformat()}
            
            # Status já está em inglês no banco: open, closed, archived
            # Não precisa mais de mapeamento
            
            # Update contact_name if provided and different
            if request.contact_name and request.contact_name != conversation.get("contact_name"):
                updates["contact_name"] = request.contact_name
                # Também atualizar title para compatibilidade
                updates["title"] = request.contact_name
            
            # Update status if provided and different
            if request.status and request.status != conversation.get("status"):
                updates["status"] = request.status
            
            # Only update if there are changes beyond updated_at
            if len(updates) > 1:
                _client.table("conversations") \
                    .update(updates) \
                    .eq("id", conversation_id) \
                    .execute()
                
                logger.info(f"Updated conversation {conversation_id} with changes: {list(updates.keys())}")
            
            return conversation_id, False
        
        else:
            # Conversation doesn't exist - create new
            started_at = None
            if request.started_at_ts:
                started_at = datetime.utcfromtimestamp(request.started_at_ts).isoformat()
            
            # Status já está em inglês: open, closed, archived
            new_conversation = {
                "user_id": request.user_id,
                "external_contact_id": request.external_contact_id,
                "contact_name": request.contact_name,
                "title": request.contact_name or "Untitled",
                "canal": request.source,  # TODO: Será 'channel' após migração SQL completa
                "status": request.status or "open",
            }
            
            if started_at:
                new_conversation["started_at"] = started_at
            
            result = _client.table("conversations") \
                .insert(new_conversation) \
                .execute()
            
            if not result.data or len(result.data) == 0:
                raise Exception("Failed to create conversation - no data returned")
            
            conversation_id = result.data[0]["id"]
            logger.info(f"Created new conversation {conversation_id} for user {request.user_id}")
            
            return conversation_id, True
            
    except Exception as e:
        logger.exception(f"Error upserting conversation: {e}")
        raise


async def get_conversation_by_contact(user_id: str, external_contact_id: str) -> Optional[str]:
    """
    Get conversation ID by user_id and external_contact_id.
    
    Args:
        user_id: User UUID
        external_contact_id: External contact identifier
        
    Returns:
        Conversation ID if found, None otherwise
    """
    try:
        result = _client.table("conversations") \
            .select("id") \
            .eq("user_id", user_id) \
            .eq("external_contact_id", external_contact_id) \
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        
        return None
        
    except Exception as e:
        logger.exception(f"Error getting conversation: {e}")
        raise

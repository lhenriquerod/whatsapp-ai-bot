"""
Conversation Service - Adaptado para estrutura existente do BD
Tabela: conversas (com campos: titulo, status, user_id, etc)
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
    Upsert a conversation record - ADAPTADO para tabela conversas existente.
    
    Args:
        request: ConversationUpsertRequest with conversation data
        
    Returns:
        Tuple of (conversation_id, created) where created indicates if it was newly created
        
    Raises:
        Exception: If database operation fails
    """
    try:
        # Tentar buscar por external_contact_id (se o campo existir)
        # Senão buscar por titulo que contém o contact_name
        existing = None
        
        # Se external_contact_id existe no BD
        if request.external_contact_id:
            try:
                existing = _client.table("conversas") \
                    .select("id, status, titulo, external_contact_id") \
                    .eq("user_id", request.user_id) \
                    .eq("external_contact_id", request.external_contact_id) \
                    .execute()
            except:
                # Campo não existe ainda, buscar por titulo
                pass
        
        # Fallback: buscar por titulo (contact_name)
        if not existing or not existing.data:
            if request.contact_name:
                existing = _client.table("conversas") \
                    .select("id, status, titulo") \
                    .eq("user_id", request.user_id) \
                    .eq("titulo", request.contact_name) \
                    .execute()
        
        if existing and existing.data and len(existing.data) > 0:
            # Conversation exists - update if needed
            conversation = existing.data[0]
            conversation_id = conversation["id"]
            
            # Prepare updates
            updates: Dict[str, Any] = {"updated_at": datetime.utcnow().isoformat()}
            
            # Mapear status: "open" -> "aberta", "closed" -> "fechada"
            db_status = {
                "open": "aberta",
                "closed": "fechada",
                "archived": "arquivada"
            }.get(request.status, "aberta")
            
            # Update status if provided and different
            if db_status and db_status != conversation.get("status"):
                updates["status"] = db_status
            
            # Update titulo (contact_name) if provided and different
            if request.contact_name and request.contact_name != conversation.get("titulo"):
                updates["titulo"] = request.contact_name
                if "contact_name" in updates:
                    updates["contact_name"] = request.contact_name
            
            # Update external_contact_id if field exists
            if request.external_contact_id:
                try:
                    updates["external_contact_id"] = request.external_contact_id
                except:
                    pass
            
            # Update source if field exists
            if request.source:
                try:
                    updates["source"] = request.source
                except:
                    pass
            
            # Only update if there are changes beyond updated_at
            if len(updates) > 1:
                _client.table("conversas") \
                    .update(updates) \
                    .eq("id", conversation_id) \
                    .execute()
                
                logger.info(f"Updated conversation {conversation_id}")
            
            return conversation_id, False
        
        else:
            # Conversation doesn't exist - create new
            iniciada_em = None
            if request.started_at_ts:
                iniciada_em = datetime.utcfromtimestamp(request.started_at_ts).isoformat()
            
            # Mapear status para valores do BD
            db_status = {
                "open": "aberta",
                "closed": "fechada",
                "archived": "arquivada"
            }.get(request.status, "aberta")
            
            new_conversation = {
                "user_id": request.user_id,
                "titulo": request.contact_name or "Sem título",
                "status": db_status,
            }
            
            # Adicionar campos opcionais se existirem no BD
            if request.external_contact_id:
                try:
                    new_conversation["external_contact_id"] = request.external_contact_id
                except:
                    pass
            
            if request.contact_name:
                try:
                    new_conversation["contact_name"] = request.contact_name
                except:
                    pass
            
            if request.source:
                try:
                    new_conversation["source"] = request.source
                except:
                    pass
            
            if iniciada_em:
                new_conversation["iniciada_em"] = iniciada_em
            
            result = _client.table("conversas") \
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
        # Tentar buscar por external_contact_id
        try:
            result = _client.table("conversas") \
                .select("id") \
                .eq("user_id", user_id) \
                .eq("external_contact_id", external_contact_id) \
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]["id"]
        except:
            # Campo não existe, tentar por titulo
            pass
        
        # Fallback: buscar por titulo
        result = _client.table("conversas") \
            .select("id") \
            .eq("user_id", user_id) \
            .eq("titulo", external_contact_id) \
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        
        return None
        
    except Exception as e:
        logger.exception(f"Error getting conversation: {e}")
        raise

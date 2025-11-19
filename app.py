"""
RAG-E Chat Service
FastAPI microservice that exposes /chat endpoint for n8n orchestration.
"""
import logging
import time
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.services.supabase_service import get_context
from src.services.ai_service import AIService
from src.services import conversation_service, message_service
from src.services.personality_service import (
    get_agent_personality,
    build_system_prompt_with_personality
)
from src.models.conversation import ConversationUpsertRequest, ConversationUpsertResponse
from src.models.message import MessageCreateRequest, MessageCreateResponse
from src.utils.config import PORT

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG-E Chat Service",
    description="Microservice for AI-powered chat with Supabase knowledge base",
    version="2.0.0"
)

# CORS middleware - TODO: restrict origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Note: AIService is now instantiated per-request with user credentials
# No global instance needed


# Request/Response models
class ChatIn(BaseModel):
    """Chat request payload"""
    user_id: str = Field(..., min_length=1, description="User identifier (owner_id in Supabase)")
    message: str = Field(..., min_length=1, description="User's message/question")
    external_contact_id: Optional[str] = Field(None, description="External contact ID (e.g., WhatsApp number) for conversation history")


class ChatOut(BaseModel):
    """Chat response payload"""
    reply: str = Field(..., description="AI-generated response")
    source: str = Field(default="supabase", description="Knowledge source used")
    request_id: Optional[str] = Field(None, description="Request tracking ID if provided")


class SimulationChatIn(BaseModel):
    """Simulation chat request payload"""
    user_id: str = Field(..., min_length=1, description="User identifier (owner_id in Supabase)")
    message: str = Field(..., min_length=1, description="User's message/question")
    external_contact_id: Optional[str] = Field(None, description="External contact ID for conversation history")


class SimulationChatOut(BaseModel):
    """Simulation chat response payload"""
    reply: str = Field(..., description="AI-generated response")
    source: str = Field(default="supabase", description="Knowledge source used")
    request_id: Optional[str] = Field(None, description="Request tracking ID if provided")


# Internal helper function
def generate_agent_reply(
    user_id: str,
    message: str,
    x_request_id: Optional[str] = None,
    external_contact_id: Optional[str] = None
) -> ChatOut:
    """
    Generate agent reply using knowledge base context and user configuration.
    
    This function is shared between /chat and /simulation/chat routes.
    Uses user-specific AI credentials instead of global .env configuration.
    
    Args:
        user_id: User identifier for fetching context and config
        message: User's message/question
        x_request_id: Optional request tracking ID
        external_contact_id: Optional external contact ID for conversation history
        
    Returns:
        ChatOut with AI-generated reply
        
    Raises:
        Exception: If context fetching or AI generation fails
    """
    # STEP 1: Fetch user's AI credentials
    from src.services.ai_credentials_service import get_user_ai_credentials, validate_credentials, get_temperature
    
    credentials = get_user_ai_credentials(user_id)
    
    if not validate_credentials(credentials):
        logger.error(f"Invalid AI credentials for user_id={user_id[-4:]}")
        raise Exception("User AI credentials not configured or invalid")
    
    # Extract credentials
    api_key = credentials.get("api_key_encrypted")
    model = credentials.get("default_model") or "gpt-4o-mini"
    temperature = get_temperature(credentials, default=0.2)
    base_url = credentials.get("base_url")
    organization_id = credentials.get("organization_id")
    provider = credentials.get("provider", "openai")
    
    logger.info(f"Using AI credentials: provider={provider} model={model} temp={temperature}")
    
    # STEP 2: Initialize AIService with user's credentials
    user_ai = AIService(
        api_key=api_key,
        base_url=base_url,
        organization_id=organization_id
    )
    
    # STEP 3: Fetch context from Supabase using vector search (with fallback)
    # Using hybrid_search: tries vector search first, falls back to original get_context()
    try:
        from src.services.vector_search import hybrid_search
        import asyncio
        
        # Run async hybrid_search (vector search with fallback)
        context = asyncio.run(hybrid_search(
            user_id=user_id,
            query=message,  # Use user's message for semantic search
            top_k=5
        ))
        
        logger.info(f"Retrieved context using hybrid search (vector + fallback)")
        
    except Exception as e:
        logger.warning(f"Hybrid search failed, using original get_context(): {e}")
        # Fallback to original implementation if vector search fails
        context = get_context(owner_id=user_id)
    
    # STEP 4: Fetch agent personality configuration
    personality = get_agent_personality(user_id)
    
    # STEP 5: Build system prompt with personality and knowledge base
    system_prompt = build_system_prompt_with_personality(context, personality)
    
    # STEP 6: Build user prompt with conversation history if available
    user_prompt = message
    contact_name = None
    
    # If we have external_contact_id, fetch conversation history
    if external_contact_id:
        from src.services.message_service import get_conversation_history
        
        logger.info(f"Fetching conversation history for contact={external_contact_id}")
        
        history, contact_name = get_conversation_history(
            user_id=user_id,
            external_contact_id=external_contact_id,
            limit=10  # Last 10 messages
        )
        
        logger.info(f"Found {len(history)} messages in history, contact_name={contact_name}")
        
        if history or contact_name:
            # Build conversation context
            history_context = "=== INFORMAÇÕES DA CONVERSA ===\n"
            
            if contact_name:
                history_context += f"Você está conversando com: {contact_name}\n"
                # Replace {{contact_name}} placeholder in system prompt
                system_prompt = system_prompt.replace('{{contact_name}}', contact_name)
            
            if history:
                history_context += "\n=== HISTÓRICO DE MENSAGENS ===\n"
                for msg in history:
                    direction = msg.get("direction", "unknown")
                    msg_text = msg.get("message", "")  # Campo 'message' em inglês
                    
                    if direction == "inbound":  # Mensagem do usuário
                        history_context += f"Usuário: {msg_text}\n"
                    elif direction == "outbound":  # Mensagem do assistente
                        history_context += f"Assistente: {msg_text}\n"
            
            history_context += "=== FIM DO HISTÓRICO ===\n\n"
            history_context += "=== MENSAGEM ATUAL ===\n"
            
            logger.info(f"History context built: {len(history_context)} chars")
            
            # Prepend history to user prompt
            user_prompt = f"{history_context}{message}"
    
    # STEP 7: Generate AI response using user's credentials
    reply = user_ai.generate_response(
        system_prompt=system_prompt, 
        user_prompt=user_prompt,
        model=model,
        temperature=temperature
    )
    
    # Normalize line breaks for WhatsApp compatibility
    # WhatsApp may need explicit \n characters, ensure they're preserved
    reply = reply.replace('\r\n', '\n')  # Normalize Windows line breaks
    
    return ChatOut(reply=reply, source="supabase", request_id=x_request_id)


# Routes
@app.get("/healthz")
def healthz():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn, x_request_id: Optional[str] = Header(default=None)):
    """
    Chat endpoint - receives user message and returns AI-generated response
    based on Supabase knowledge base context.
    
    Includes automatic name collection flow for new contacts.
    
    Args:
        payload: ChatIn with user_id and message
        x_request_id: Optional request tracking header
        
    Returns:
        ChatOut with reply, source, and request_id
        
    Raises:
        HTTPException: 500 if internal error occurs
    """
    start = time.time()
    
    try:
        # Mask user_id for logging (privacy)
        masked_user = f"***{payload.user_id[-4:]}" if len(payload.user_id) > 4 else "***"
        logger.info("chat_start user=%s request_id=%s", masked_user, x_request_id)
        
        # STEP 1: Check if we need to collect contact name
        # This handles the name collection flow (AWAITING_NAME, CONFIRMING_NAME states)
        if payload.external_contact_id:
            from src.services.name_collection_service import process_name_collection_flow
            
            response_text, should_continue_to_ai = process_name_collection_flow(
                message_text=payload.message,
                external_contact_id=payload.external_contact_id,
                user_id=payload.user_id
            )
            
            # If name collection flow handled the message, return its response
            if not should_continue_to_ai:
                elapsed_ms = int((time.time() - start) * 1000)
                logger.info("chat_name_collection user=%s elapsed_ms=%d", masked_user, elapsed_ms)
                return ChatOut(
                    reply=response_text,
                    source="name_collection",
                    request_id=x_request_id
                )
        
        # STEP 2: Process with AI (name already collected or no external_contact_id)
        result = generate_agent_reply(
            user_id=payload.user_id,
            message=payload.message,
            x_request_id=x_request_id,
            external_contact_id=payload.external_contact_id
        )
        
        elapsed_ms = int((time.time() - start) * 1000)
        logger.info("chat_success user=%s request_id=%s elapsed_ms=%d", masked_user, x_request_id, elapsed_ms)
        
        return result
        
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        logger.exception("chat_error request_id=%s elapsed_ms=%d error=%s", x_request_id, elapsed_ms, str(e))
        raise HTTPException(status_code=500, detail="internal_error")


@app.post("/simulation/chat", response_model=SimulationChatOut)
def simulation_chat(payload: SimulationChatIn, x_request_id: Optional[str] = Header(default=None)):
    """
    Simulation chat endpoint - for testing the agent without WhatsApp integration.
    
    This endpoint is designed for the web panel's "Simulation Mode" where users can
    test their agent's responses without creating conversation or message records.
    
    The endpoint:
    - Fetches knowledge base context from Supabase
    - Uses user's configuration (personalidade_agente, tom_voz)
    - Generates AI response using the same logic as /chat
    - Does NOT create records in conversas or mensagens tables
    
    Args:
        payload: SimulationChatIn with user_id and message
        x_request_id: Optional request tracking header
        
    Returns:
        SimulationChatOut with AI reply
        
    Raises:
        HTTPException: 500 if internal error occurs
        
    Example Request:
        POST /simulation/chat
        {
          "user_id": "6bf0dab0-e895-4730-b5fa-cd8acff6de0c",
          "message": "Olá, quero testar meu agente."
        }
        
    Example Response:
        {
          "reply": "Olá! Aqui é o agente em modo simulação. Como posso ajudá-lo?",
          "source": "supabase",
          "request_id": "abc-123"
        }
    """
    start = time.time()
    
    try:
        # Mask user_id for logging (privacy)
        masked_user = f"***{payload.user_id[-4:]}" if len(payload.user_id) > 4 else "***"
        logger.info("chat_simulation_start user=%s request_id=%s", masked_user, x_request_id)
        
        # Generate reply using shared logic (same as /chat)
        result = generate_agent_reply(
            user_id=payload.user_id,
            message=payload.message,
            x_request_id=x_request_id,
            external_contact_id=payload.external_contact_id  # Include conversation context
        )

        elapsed_ms = int((time.time() - start) * 1000)
        logger.info("chat_simulation_success user=%s request_id=%s elapsed_ms=%d", masked_user, x_request_id, elapsed_ms)

        return SimulationChatOut(
            reply=result.reply,
            source=result.source,
            request_id=result.request_id
        )

    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        logger.exception("chat_simulation_error request_id=%s elapsed_ms=%d error=%s", x_request_id, elapsed_ms, str(e))
        raise HTTPException(status_code=500, detail="internal_error")


@app.post("/conversations/upsert", response_model=ConversationUpsertResponse, status_code=200)
async def upsert_conversation(payload: ConversationUpsertRequest):
    """
    Upsert a conversation - create if doesn't exist, update if exists.
    
    This endpoint ensures a conversation record exists for a given user and contact.
    If the conversation already exists, it updates fields like contact_name and status.
    
    Args:
        payload: ConversationUpsertRequest with conversation data
        
    Returns:
        ConversationUpsertResponse with conversation_id and created flag
        
    Raises:
        HTTPException: 400 for validation errors, 500 for internal errors
    """
    try:
        logger.info(
            f"upsert_conversation user_id={payload.user_id} "
            f"contact={payload.external_contact_id} source={payload.source}"
        )

        conversation_id, created = await conversation_service.upsert_conversation(payload)

        return ConversationUpsertResponse(
            conversation_id=conversation_id,
            created=created
        )

    except Exception as e:
        logger.exception(f"Error in upsert_conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@app.post("/messages", response_model=MessageCreateResponse, status_code=201)
async def create_message(payload: MessageCreateRequest):
    """
    Create a new message in a conversation.
    
    If conversation_id is not provided, it will be resolved by looking up
    or creating a conversation for the given user_id and external_contact_id.
    
    Args:
        payload: MessageCreateRequest with message data
        
    Returns:
        MessageCreateResponse with message_id and conversation_id
        
    Raises:
        HTTPException: 400 for validation errors, 500 for internal errors
    """
    try:
        logger.info(
            f"create_message user_id={payload.user_id} "
            f"contact={payload.external_contact_id} "
            f"direction={payload.direction} type={payload.type}"
        )
        
        message_id, conversation_id = await message_service.create_message(payload)
        
        return MessageCreateResponse(
            message_id=message_id,
            conversation_id=conversation_id
        )
        
    except ValueError as e:
        # Validation errors (e.g., invalid conversation_id)
        logger.warning(f"Validation error in create_message: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error in create_message: {e}")
        raise HTTPException(status_code=500, detail="internal_error")


# ============================================================================
# Knowledge Processing Endpoints (RAG with Vector Embeddings)
# ============================================================================

class KnowledgeProcessResponse(BaseModel):
    """Response from knowledge processing endpoint"""
    message: str
    knowledge_entries: int
    chunks_created: int
    processing_time_ms: int


@app.post("/knowledge/process-chunks/{user_id}", response_model=KnowledgeProcessResponse)
async def process_knowledge_chunks(user_id: str):
    """
    Process all knowledge_base entries for a user into chunks with embeddings.
    
    This endpoint:
    1. Fetches all knowledge_base entries for the user
    2. Splits them into chunks (500 chars with 100 char overlap)
    3. Generates embeddings using OpenAI
    4. Stores chunks in knowledge_chunks table
    
    Call this after the user creates/updates knowledge base entries.
    Can be called from frontend or triggered automatically.
    
    Args:
        user_id: User UUID
        
    Returns:
        KnowledgeProcessResponse with processing stats
        
    Raises:
        HTTPException: 500 if processing fails
    """
    start = time.time()
    
    try:
        logger.info(f"Processing knowledge chunks for user {user_id[-4:]}")
        
        from src.services.supabase_service import _client
        from src.services.chunking import split_into_chunks, prepare_knowledge_for_chunking
        from src.services.embeddings import generate_embeddings_batch
        
        # 1. Fetch all knowledge_base entries for the user
        result = _client.table('knowledge_base')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        knowledge_entries = result.data or []
        
        if not knowledge_entries:
            elapsed_ms = int((time.time() - start) * 1000)
            logger.info(f"No knowledge entries found for user {user_id[-4:]}")
            return KnowledgeProcessResponse(
                message="Nenhuma entrada encontrada na base de conhecimento",
                knowledge_entries=0,
                chunks_created=0,
                processing_time_ms=elapsed_ms
            )
        
        # 2. Delete old chunks for this user (reprocess everything)
        _client.table('knowledge_chunks')\
            .delete()\
            .eq('owner_id', user_id)\
            .execute()
        
        logger.info(f"Cleared old chunks for user {user_id[-4:]}")
        
        all_chunks = []
        
        # 3. For each knowledge entry, prepare text and split into chunks
        for entry in knowledge_entries:
            # Prepare formatted text
            full_text = prepare_knowledge_for_chunking(entry)
            
            # Split into chunks
            chunks = split_into_chunks(full_text, chunk_size=500, chunk_overlap=100)
            
            # Prepare chunk records
            for chunk_text in chunks:
                all_chunks.append({
                    'owner_id': user_id,
                    'knowledge_id': entry.get('id'),
                    'category': entry.get('category'),
                    'source': 'dashboard',
                    'chunk_text': chunk_text
                })
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(knowledge_entries)} entries")
        
        if not all_chunks:
            elapsed_ms = int((time.time() - start) * 1000)
            return KnowledgeProcessResponse(
                message="Nenhum chunk foi criado",
                knowledge_entries=len(knowledge_entries),
                chunks_created=0,
                processing_time_ms=elapsed_ms
            )
        
        # 4. Generate embeddings in batch
        chunk_texts = [c['chunk_text'] for c in all_chunks]
        embeddings = await generate_embeddings_batch(chunk_texts)
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # 5. Add embeddings to chunk records
        for i, chunk in enumerate(all_chunks):
            chunk['embedding'] = embeddings[i]
        
        # 6. Insert all chunks into knowledge_chunks table
        _client.table('knowledge_chunks')\
            .insert(all_chunks)\
            .execute()
        
        elapsed_ms = int((time.time() - start) * 1000)
        
        logger.info(
            f"Processed knowledge for user {user_id[-4:]}: "
            f"{len(knowledge_entries)} entries → {len(all_chunks)} chunks "
            f"in {elapsed_ms}ms"
        )
        
        return KnowledgeProcessResponse(
            message="Chunks processados e embeddings gerados com sucesso",
            knowledge_entries=len(knowledge_entries),
            chunks_created=len(all_chunks),
            processing_time_ms=elapsed_ms
        )
        
    except Exception as e:
        logger.exception(f"Error processing knowledge chunks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar chunks: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting RAG-E Chat Service on port %s", PORT)
    uvicorn.run(app, host="0.0.0.0", port=PORT)

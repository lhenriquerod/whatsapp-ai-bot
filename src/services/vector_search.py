"""
Vector Search Service
Performs semantic search using embeddings and pgvector.
"""
import logging
from typing import List, Dict, Optional
from supabase import Client

from src.services.embeddings import generate_embedding
from src.services.supabase_service import _client

logger = logging.getLogger(__name__)


async def search_similar_chunks(
    user_id: str,
    query: str,
    top_k: int = 5,
    category: Optional[str] = None,
    similarity_threshold: float = 0.7
) -> List[Dict]:
    """
    Search for the most similar knowledge chunks using vector embeddings.
    
    Args:
        user_id: User ID for tenant isolation
        query: User's question/query
        top_k: Number of most relevant chunks to return
        category: Optional filter by category (product, faq, company, etc.)
        similarity_threshold: Minimum similarity score (0-1, where 1 is identical)
    
    Returns:
        List of dicts with chunk data and similarity scores:
        [
            {
                "id": "uuid",
                "chunk_text": "...",
                "category": "product",
                "source": "dashboard",
                "similarity": 0.89,
                "knowledge_id": "uuid..."
            },
            ...
        ]
    
    Example:
        >>> chunks = await search_similar_chunks(
        ...     user_id="...",
        ...     query="Does the Essential plan have a free trial?",
        ...     top_k=3
        ... )
        >>> len(chunks) <= 3
        True
        >>> chunks[0]['similarity'] >= 0.7
        True
    """
    try:
        logger.info(f"Searching chunks for user {user_id[-4:]}, query: '{query[:50]}...'")
        
        # 1. Generate embedding for the query
        query_embedding = await generate_embedding(query)
        
        # 2. Call Supabase RPC function for vector search
        params = {
            'query_embedding': query_embedding,
            'match_count': top_k,
            'filter_user_id': user_id,
            'similarity_threshold': similarity_threshold
        }
        
        if category:
            params['filter_category'] = category
        
        result = _client.rpc('match_knowledge_chunks', params).execute()
        
        chunks = result.data if result.data else []
        
        logger.info(f"Found {len(chunks)} similar chunks (threshold: {similarity_threshold})")
        
        return chunks
        
    except Exception as e:
        logger.exception(f"Error searching similar chunks: {e}")
        # Return empty list instead of raising to allow graceful degradation
        return []


async def get_context_from_chunks(
    user_id: str,
    query: str,
    category: Optional[str] = None,
    top_k: int = 5,
    similarity_threshold: float = 0.7
) -> str:
    """
    Main function that replaces the original get_context().
    Returns formatted string to be used as context in LLM prompt.
    
    This function:
    1. Searches for semantically similar chunks
    2. Formats them into a readable context string
    3. Returns the context for inclusion in the AI prompt
    
    Args:
        user_id: User ID
        query: User's question (used for semantic search)
        category: Optional category filter
        top_k: Number of chunks to include in context
        similarity_threshold: Minimum similarity score
    
    Returns:
        Formatted context string for the LLM
        
    Example:
        >>> context = await get_context_from_chunks(
        ...     user_id="...",
        ...     query="Tell me about pricing",
        ...     top_k=3
        ... )
        >>> "Base de Conhecimento" in context
        True
    """
    try:
        chunks = await search_similar_chunks(
            user_id=user_id,
            query=query,
            top_k=top_k,
            category=category,
            similarity_threshold=similarity_threshold
        )
        
        if not chunks:
            logger.warning(f"No relevant chunks found for user {user_id[-4:]}")
            return "Nenhuma informação relevante encontrada na base de conhecimento."
        
        # Format chunks as context
        context_parts = ["=== BASE DE CONHECIMENTO (Busca Semântica) ===\n"]
        
        for i, chunk in enumerate(chunks, 1):
            category_label = chunk.get('category', 'geral').upper()
            text = chunk.get('chunk_text', '')
            similarity = chunk.get('similarity', 0)
            
            # Format with relevance indicator
            context_parts.append(
                f"{i}. [{category_label}] (relevância: {similarity:.0%})\n{text}\n"
            )
        
        context = "\n".join(context_parts)
        
        logger.debug(f"Built context with {len(chunks)} chunks ({len(context)} chars)")
        
        return context
        
    except Exception as e:
        logger.exception(f"Error getting context from chunks: {e}")
        return "Erro ao buscar informações na base de conhecimento."


async def hybrid_search(
    user_id: str,
    query: str,
    category: Optional[str] = None,
    top_k: int = 5
) -> str:
    """
    Hybrid search: tries vector search first, falls back to original get_context().
    
    This allows gradual migration - if no chunks are found in knowledge_chunks,
    falls back to the original knowledge_base table.
    
    Args:
        user_id: User ID
        query: User's question
        category: Optional category filter
        top_k: Number of results
    
    Returns:
        Context string from vector search or fallback
    """
    try:
        # Try vector search first
        context = await get_context_from_chunks(
            user_id=user_id,
            query=query,
            category=category,
            top_k=top_k,
            similarity_threshold=0.7
        )
        
        # Check if vector search found anything
        if "Nenhuma informação relevante" not in context and "Erro ao buscar" not in context:
            logger.info("Using vector search results")
            return context
        
        # Fall back to original get_context
        logger.info("Vector search empty, falling back to original get_context()")
        from src.services.supabase_service import get_context as original_get_context
        
        return original_get_context(user_id)
        
    except Exception as e:
        logger.exception(f"Error in hybrid search: {e}")
        # Last resort fallback
        from src.services.supabase_service import get_context as original_get_context
        return original_get_context(user_id)

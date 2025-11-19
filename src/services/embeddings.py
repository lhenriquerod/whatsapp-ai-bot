"""
Embeddings Service
Generates vector embeddings using OpenAI API for semantic search.
"""
import logging
from typing import List
from openai import AsyncOpenAI
from src.utils.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Default embedding model (1536 dimensions)
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


async def generate_embedding(text: str, model: str = DEFAULT_EMBEDDING_MODEL) -> List[float]:
    """
    Generate embedding vector for a single text using OpenAI API.
    
    Args:
        text: Text to generate embedding for
        model: OpenAI embedding model (default: text-embedding-3-small = 1536 dims)
    
    Returns:
        List of floats representing the embedding vector
        
    Example:
        >>> embedding = await generate_embedding("What is the Essential Plan?")
        >>> len(embedding)
        1536
    """
    try:
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding generation")
            return [0.0] * 1536  # Return zero vector for empty text
        
        response = await client.embeddings.create(
            model=model,
            input=text.strip()
        )
        
        embedding = response.data[0].embedding
        logger.debug(f"Generated embedding for text (length: {len(text)}, dims: {len(embedding)})")
        
        return embedding
        
    except Exception as e:
        logger.exception(f"Failed to generate embedding: {e}")
        raise


async def generate_embeddings_batch(
    texts: List[str], 
    model: str = DEFAULT_EMBEDDING_MODEL
) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in a single API call.
    More efficient than calling generate_embedding() multiple times.
    
    OpenAI allows up to 2048 texts per batch.
    
    Args:
        texts: List of texts to generate embeddings for
        model: OpenAI embedding model (default: text-embedding-3-small)
    
    Returns:
        List of embedding vectors, one per input text
        
    Example:
        >>> texts = ["Product A", "Product B", "Product C"]
        >>> embeddings = await generate_embeddings_batch(texts)
        >>> len(embeddings)
        3
        >>> len(embeddings[0])
        1536
    """
    try:
        if not texts:
            logger.warning("Empty texts list provided for batch embedding generation")
            return []
        
        # Filter out empty texts but keep track of original indices
        valid_texts = []
        valid_indices = []
        
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text.strip())
                valid_indices.append(i)
        
        if not valid_texts:
            logger.warning("All texts were empty after filtering")
            return [[0.0] * 1536] * len(texts)
        
        # OpenAI limit is 2048 texts per batch
        if len(valid_texts) > 2048:
            logger.warning(f"Batch size {len(valid_texts)} exceeds limit, processing in chunks")
            
            # Process in chunks of 2048
            all_embeddings = []
            for i in range(0, len(valid_texts), 2048):
                chunk = valid_texts[i:i + 2048]
                response = await client.embeddings.create(
                    model=model,
                    input=chunk
                )
                all_embeddings.extend([item.embedding for item in response.data])
        else:
            response = await client.embeddings.create(
                model=model,
                input=valid_texts
            )
            all_embeddings = [item.embedding for item in response.data]
        
        # Reconstruct full list with zero vectors for empty texts
        result = []
        valid_idx = 0
        
        for i in range(len(texts)):
            if i in valid_indices:
                result.append(all_embeddings[valid_idx])
                valid_idx += 1
            else:
                result.append([0.0] * 1536)  # Zero vector for empty text
        
        logger.info(f"Generated {len(result)} embeddings in batch")
        
        return result
        
    except Exception as e:
        logger.exception(f"Failed to generate batch embeddings: {e}")
        raise

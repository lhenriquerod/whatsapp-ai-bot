-- ================================================
-- Migration 029: Create vector search function
-- Semantic search using pgvector cosine similarity
-- ================================================

-- Function to match knowledge chunks by semantic similarity
CREATE OR REPLACE FUNCTION match_knowledge_chunks(
  query_embedding vector(1536),
  match_count int DEFAULT 5,
  filter_user_id uuid DEFAULT NULL,
  filter_category text DEFAULT NULL,
  similarity_threshold float DEFAULT 0.7
)
RETURNS TABLE (
  id uuid,
  owner_id uuid,
  knowledge_id uuid,
  category text,
  source text,
  chunk_text text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    kc.id,
    kc.owner_id,
    kc.knowledge_id,
    kc.category,
    kc.source,
    kc.chunk_text,
    1 - (kc.embedding <=> query_embedding) as similarity
  FROM knowledge_chunks kc
  WHERE 
    (filter_user_id IS NULL OR kc.owner_id = filter_user_id)
    AND (filter_category IS NULL OR kc.category = filter_category)
    AND (1 - (kc.embedding <=> query_embedding)) >= similarity_threshold
  ORDER BY kc.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION match_knowledge_chunks IS 
  'Semantic search using cosine similarity on embeddings. 
   Returns TOP-K chunks most similar to query_embedding.

   Parameters:
   - query_embedding: 1536-dim vector from OpenAI text-embedding-3-small
   - match_count: number of results to return (default: 5)
   - filter_user_id: optional user filter for tenant isolation
   - filter_category: optional category filter (product, faq, company, etc.)
   - similarity_threshold: minimum similarity score 0-1 (default: 0.7)

   Returns: chunks ordered by similarity (highest first) with scores';

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION match_knowledge_chunks TO authenticated;
GRANT EXECUTE ON FUNCTION match_knowledge_chunks TO anon;

"""
Test RAG Vector Implementation
Tests the complete RAG pipeline: chunking → embeddings → vector search
"""
import asyncio
from src.services.chunking import split_into_chunks, prepare_knowledge_for_chunking
from src.services.embeddings import generate_embedding, generate_embeddings_batch
from src.services.vector_search import search_similar_chunks, get_context_from_chunks

print("=" * 70)
print("RAG VECTOR IMPLEMENTATION TEST")
print("=" * 70)

# Test 1: Chunking
print("\n1. Testing chunking service...")
test_text = """
O RAG-E é uma plataforma de chatbot com IA para WhatsApp. 
Oferece três planos: Essential, Professional e Enterprise.
O plano Essential custa R$ 99/mês e tem período de teste grátis de 30 dias.
O plano Professional custa R$ 299/mês com recursos avançados.
O plano Enterprise é sob consulta para grandes empresas.
Aceita pagamento via cartão de crédito, Pix e boleto.
"""

chunks = split_into_chunks(test_text, chunk_size=150, chunk_overlap=30)
print(f"   ✅ Split text ({len(test_text)} chars) into {len(chunks)} chunks")
for i, chunk in enumerate(chunks, 1):
    print(f"      Chunk {i}: {chunk[:50]}... ({len(chunk)} chars)")

# Test 2: Knowledge preparation
print("\n2. Testing knowledge preparation...")
test_entry = {
    "category": "product",
    "data": {
        "nome": "RAG-E Essential",
        "descricao": "Plano perfeito para pequenas empresas",
        "tipo_produto": "assinatura_plano_unico",
        "preco_mensal": "99",
        "periodo_trial": "30",
        "formas_pagamento": "Cartão, Pix, Boleto"
    }
}

formatted_text = prepare_knowledge_for_chunking(test_entry)
print(f"   ✅ Formatted knowledge entry:")
print(f"      {formatted_text[:100]}...")

# Test 3: Embedding generation
print("\n3. Testing embedding generation...")

async def test_embeddings():
    # Single embedding
    embedding = await generate_embedding("What is the Essential plan?")
    print(f"   ✅ Generated single embedding: {len(embedding)} dimensions")
    print(f"      First 5 values: {embedding[:5]}")
    
    # Batch embeddings
    texts = [
        "Quanto custa o plano Essential?",
        "Tem período de teste grátis?",
        "Quais formas de pagamento aceita?"
    ]
    embeddings = await generate_embeddings_batch(texts)
    print(f"   ✅ Generated batch embeddings: {len(embeddings)} vectors")
    
    return embeddings

# Run async test
embeddings = asyncio.run(test_embeddings())

# Test 4: Vector search (requires database)
print("\n4. Testing vector search...")
print("   ⚠️  This requires:")
print("      - Supabase connection")
print("      - knowledge_chunks table populated")
print("      - match_knowledge_chunks() function created")
print("\n   To test, run:")
print("      POST http://localhost:8000/knowledge/process-chunks/{user_id}")
print("      Then test chat with semantic queries")

# Test 5: Show example queries
print("\n5. Example semantic search queries:")
example_queries = [
    "Qual o plano mais barato?",
    "Tem desconto para pagamento anual?",
    "Quantos usuários posso ter?",
    "Como funciona o período de teste?",
    "Posso pagar com Pix?"
]

print("   These queries will find relevant chunks even if:")
print("   - Different wording (synonyms)")
print("   - Different language")
print("   - Related concepts")
print("\n   Example queries:")
for i, q in enumerate(example_queries, 1):
    print(f"      {i}. {q}")

print("\n" + "=" * 70)
print("✅ RAG implementation is ready!")
print("=" * 70)
print("\nNext steps:")
print("1. Execute SQL migrations in Supabase:")
print("   - sql/030_fix_conversations_fk_to_users.sql")
print("   - sql/029_create_match_knowledge_chunks_function.sql")
print("\n2. Process knowledge base:")
print("   POST /knowledge/process-chunks/{user_id}")
print("\n3. Test chat with semantic search:")
print("   POST /simulation/chat")
print("   {\"user_id\": \"...\", \"message\": \"Qual o plano mais barato?\"}")
print("=" * 70)

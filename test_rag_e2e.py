"""
End-to-End RAG Test
Tests the complete flow: process chunks → semantic search → chat
"""
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "e35af3a4-a7e6-422f-a483-bbcfc9d7c24f"

print("=" * 70)
print("RAG END-TO-END TEST")
print("=" * 70)

# Step 1: Process knowledge base into chunks
print("\n1. Processing knowledge base into chunks...")
print(f"   POST {BASE_URL}/knowledge/process-chunks/{USER_ID}")

try:
    response = requests.post(f"{BASE_URL}/knowledge/process-chunks/{USER_ID}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success!")
        print(f"      Knowledge entries: {data['knowledge_entries']}")
        print(f"      Chunks created: {data['chunks_created']}")
        print(f"      Processing time: {data['processing_time_ms']}ms")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"      {response.text}")
        print("\n   Possible causes:")
        print("      - Server not running (uvicorn)")
        print("      - SQL migrations not executed in Supabase")
        print("      - No knowledge_base entries for this user")
        exit(1)
        
except Exception as e:
    print(f"   ❌ Connection error: {e}")
    print("\n   Make sure uvicorn is running:")
    print("      uvicorn app:app --reload")
    exit(1)

# Step 2: Test semantic search via chat
print("\n2. Testing semantic search in chat...")

test_queries = [
    "O RAG-E tem período de teste grátis?",
    "Qual o plano mais barato?",
    "Quantos usuários posso ter?",
    "Aceita pagamento com Pix?"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n   Query {i}: {query}")
    
    payload = {
        "user_id": USER_ID,
        "message": query
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/simulation/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")
            print(f"   ✅ Response ({len(reply)} chars):")
            print(f"      {reply[:150]}...")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"      {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Step 3: Verify logs
print("\n" + "=" * 70)
print("3. Check uvicorn terminal logs for:")
print("=" * 70)
print("   ✅ 'Using vector search results' - Vector search worked")
print("   ⚠️  'falling back to original get_context()' - No chunks found")
print("   ✅ 'Generated X embeddings in batch' - Embeddings created")
print("   ✅ 'Found X similar chunks' - Semantic search successful")

print("\n" + "=" * 70)
print("Test completed!")
print("=" * 70)

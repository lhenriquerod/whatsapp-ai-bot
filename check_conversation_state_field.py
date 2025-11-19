"""
Verifica se o campo conversation_state existe na tabela conversations
"""
from src.services.supabase_service import _client

print("Verificando schema da tabela conversations...")

try:
    # Tentar buscar com o campo conversation_state
    result = _client.table("conversations") \
        .select("id, conversation_state, contact_name, status") \
        .limit(1) \
        .execute()
    
    print("✅ Campo 'conversation_state' existe!")
    print(f"   Registros encontrados: {len(result.data)}")
    
    if result.data:
        print(f"   Exemplo de dados: {result.data[0]}")
    
except Exception as e:
    error_msg = str(e)
    
    if "conversation_state" in error_msg and "does not exist" in error_msg:
        print("❌ Campo 'conversation_state' NÃO existe!")
        print("\n📝 SQL necessário:")
        print("""
-- Adicionar campo conversation_state
ALTER TABLE conversations 
ADD COLUMN IF NOT EXISTS conversation_state VARCHAR(50) DEFAULT 'ACTIVE';

-- Criar índice para performance
CREATE INDEX IF NOT EXISTS idx_conversations_state 
ON conversations(conversation_state);

-- Comentário explicativo
COMMENT ON COLUMN conversations.conversation_state IS 
'Estado do fluxo de conversa: AWAITING_NAME, CONFIRMING_NAME, ACTIVE';
""")
    else:
        print(f"❌ Erro inesperado: {e}")

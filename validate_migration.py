"""
Script de validação da migração Backend PT→EN
Testa se as queries Supabase estão usando os nomes corretos em inglês
"""
import sys
from src.services.supabase_service import _client

print("=" * 60)
print("VALIDAÇÃO DA MIGRAÇÃO: BACKEND PT→EN")
print("=" * 60)
print()

# Teste 1: Verificar se tabelas em inglês existem
print("1. Verificando tabelas em inglês...")
try:
    # Tentar query em conversations
    result = _client.table("conversations").select("id").limit(1).execute()
    print("   ✅ Tabela 'conversations' acessível")
except Exception as e:
    print(f"   ❌ Erro ao acessar 'conversations': {e}")
    sys.exit(1)

try:
    # Tentar query em messages
    result = _client.table("messages").select("id").limit(1).execute()
    print("   ✅ Tabela 'messages' acessível")
except Exception as e:
    print(f"   ❌ Erro ao acessar 'messages': {e}")
    sys.exit(1)

try:
    # Tentar query em knowledge_base
    result = _client.table("knowledge_base").select("id").limit(1).execute()
    print("   ✅ Tabela 'knowledge_base' acessível")
except Exception as e:
    print(f"   ❌ Erro ao acessar 'knowledge_base': {e}")
    sys.exit(1)

try:
    # Tentar query em agent_personality
    result = _client.table("agent_personality").select("id").limit(1).execute()
    print("   ✅ Tabela 'agent_personality' acessível")
except Exception as e:
    print(f"   ❌ Erro ao acessar 'agent_personality': {e}")
    sys.exit(1)

print()

# Teste 2: Verificar campos em inglês
print("2. Verificando campos em inglês...")
try:
    # Campos de conversations
    result = _client.table("conversations").select("title, canal, status").limit(1).execute()
    print("   ✅ Campos 'title, canal, status' em conversations")
except Exception as e:
    print(f"   ❌ Erro nos campos de conversations: {e}")
    sys.exit(1)

try:
    # Campos de messages
    result = _client.table("messages").select("conversation_id, type, message").limit(1).execute()
    print("   ✅ Campos 'conversation_id, type, message' em messages")
except Exception as e:
    print(f"   ❌ Erro nos campos de messages: {e}")
    sys.exit(1)

try:
    # Campos de knowledge_base
    result = _client.table("knowledge_base").select("category, data").limit(1).execute()
    print("   ✅ Campos 'category, data' em knowledge_base")
except Exception as e:
    print(f"   ❌ Erro nos campos de knowledge_base: {e}")
    sys.exit(1)

try:
    # Campos de agent_personality
    result = _client.table("agent_personality").select("name, personality_level, voice_tone").limit(1).execute()
    print("   ✅ Campos 'name, personality_level, voice_tone' em agent_personality")
except Exception as e:
    print(f"   ❌ Erro nos campos de agent_personality: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO")
print("Todas as tabelas e campos em inglês estão acessíveis!")
print("=" * 60)

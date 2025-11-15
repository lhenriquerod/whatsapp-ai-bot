"""
Teste: Histórico de Conversa
Testa se o agente consegue acessar o histórico de mensagens
"""
import sys
sys.path.insert(0, '.')

from src.services.supabase_service import _client
from src.services.message_service import get_conversation_history

USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"
EXTERNAL_CONTACT = "teste-simulacao"

print("=" * 70)
print("Teste: Histórico de Conversa")
print("=" * 70)
print()

# =====================================================================
# STEP 1: Buscar/criar conversa
# =====================================================================
print("1. Buscando/criando conversa...")
try:
    # Buscar conversa existente primeiro
    conv_check = _client.table("conversas") \
        .select("id") \
        .eq("user_id", USER_ID) \
        .eq("external_contact_id", EXTERNAL_CONTACT) \
        .execute()
    
    if not conv_check.data:
        # Criar nova
        conv_result = _client.table("conversas").insert({
            "user_id": USER_ID,
            "external_contact_id": EXTERNAL_CONTACT,
            "contact_name": "Teste Simulação",
            "source": "simulacao"
            # status será o default
        }).execute()
        conversation_id = conv_result.data[0]['id']
        print("✅ Nova conversa criada")
    else:
        conversation_id = conv_check.data[0]['id']
        print("✅ Conversa existente encontrada")
    
    print(f"   Conversation ID: {conversation_id}")
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

print()

# =====================================================================
# STEP 2: Limpar mensagens antigas desta conversa
# =====================================================================
print("2. Limpando mensagens antigas...")
try:
    _client.table("mensagens").delete().eq("conversa_id", conversation_id).execute()
    print("✅ Mensagens antigas removidas")
except Exception as e:
    print(f"⚠️  Erro: {e}")
print()

# =====================================================================
# STEP 3: Inserir mensagens de exemplo
# =====================================================================
print("3. Inserindo mensagens de exemplo...")

mensagens = [
    {"direction": "incoming", "tipo": "usuario", "text": "Olá, meu nome é Lucas"},
    {"direction": "outgoing", "tipo": "agente", "text": "Olá Lucas! Prazer em conhecê-lo. Como posso ajudar?"},
    {"direction": "incoming", "tipo": "usuario", "text": "Quais planos vocês têm?"},
    {"direction": "outgoing", "tipo": "agente", "text": "Temos o Plano Essencial por R$ 260/mês..."},
]

for msg in mensagens:
    try:
        _client.table("mensagens").insert({
            "conversa_id": conversation_id,
            "direction": msg["direction"],
            "tipo": msg["tipo"],
            "mensagem": msg["text"],
            "user_id": USER_ID
        }).execute()
        label = "Usuário" if msg["tipo"] == "usuario" else "Assistente"
        print(f"   ✅ {label}: {msg['text'][:30]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print()

# =====================================================================
# STEP 4: Buscar histórico
# =====================================================================
print("4. Buscando histórico de mensagens...")
history = get_conversation_history(USER_ID, EXTERNAL_CONTACT, limit=10)

print(f"   Encontradas: {len(history)} mensagens")
print()

if history:
    print("HISTÓRICO:")
    print("-" * 70)
    for msg in history:
        direction = msg.get('direction', 'unknown')
        role = "👤 Usuário" if direction == 'incoming' else "🤖 Assistente"
        print(f"{role}: {msg.get('mensagem', '')}")
    print("-" * 70)
else:
    print("❌ Nenhuma mensagem encontrada")

print()

# =====================================================================
# STEP 5: Testar via API
# =====================================================================
print("=" * 70)
print("5. Testando via API com histórico")
print("=" * 70)
print()

import requests

print("Enviando: 'Você sabe meu nome?'")
print()

response = requests.post(
    "http://localhost:8000/simulation/chat",
    json={
        "user_id": USER_ID,
        "message": "Você sabe meu nome?",
        "external_contact_id": EXTERNAL_CONTACT  # 🔑 Importante!
    }
)

if response.status_code == 200:
    data = response.json()
    reply = data.get("reply", "")
    
    print("RESPOSTA DO AGENTE:")
    print("-" * 70)
    print(reply)
    print("-" * 70)
    print()
    
    if "Lucas" in reply or "lucas" in reply.lower():
        print("✅ SUCESSO! O agente lembrou do nome!")
    else:
        print("⚠️  O agente não mencionou o nome...")
        print("   (mas pode ter respondido de outra forma)")
else:
    print(f"❌ Erro na API: {response.status_code}")
    print(response.text)

print()
print("=" * 70)
print("Teste concluído!")
print("=" * 70)
print()
print("💡 Dica: Para que o frontend use o histórico, envie:")
print('   { "user_id": "...", "message": "...", "external_contact_id": "..." }')
print()

"""
Teste final: verificar se o agente sabe o nome do contato via contact_name
"""
import requests
import sys
sys.path.insert(0, '.')

from src.services.supabase_service import _client

BASE_URL = "http://localhost:8000"

# Usar a conversa real do WhatsApp
USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"
EXTERNAL_CONTACT = "5516988310379"  # Número do WhatsApp do Lucas

print("=" * 70)
print("Teste Final: Agente deve saber o nome via contact_name")
print("=" * 70)
print()

# Verificar qual é o nome cadastrado
print("1. Verificando nome cadastrado na conversa...")
conv = _client.table("conversas").select("contact_name").eq("user_id", USER_ID).eq("external_contact_id", EXTERNAL_CONTACT).execute()

if conv.data:
    contact_name = conv.data[0].get('contact_name')
    print(f"✅ Nome cadastrado: {contact_name}")
else:
    print("❌ Conversa não encontrada!")
    exit(1)

print()

# Testar endpoint /chat
print("2. Testando endpoint /chat...")
payload = {
    "user_id": USER_ID,
    "message": "Qual é meu nome?",
    "external_contact_id": EXTERNAL_CONTACT
}

response = requests.post(f"{BASE_URL}/chat", json=payload)

if response.status_code == 200:
    data = response.json()
    print()
    print("RESPOSTA DO AGENTE:")
    print("-" * 70)
    print(data['reply'])
    print("-" * 70)
    print()
    
    # Verificar se mencionou o nome (case insensitive)
    reply_lower = data['reply'].lower()
    name_parts = contact_name.lower().split()
    
    found_name = any(part in reply_lower for part in name_parts if len(part) > 2)
    
    if found_name:
        print(f"✅ SUCESSO! O agente mencionou o nome '{contact_name}'")
    else:
        print(f"❌ O agente NÃO mencionou o nome '{contact_name}'")
        print(f"   Esperado: Nome cadastrado na tabela conversas")
else:
    print(f"❌ Erro {response.status_code}: {response.text}")

print()
print("=" * 70)

"""
Teste do endpoint /chat com external_contact_id para memória de conversa
"""
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"
EXTERNAL_CONTACT = "5511999887766"  # Simula número WhatsApp

print("=" * 70)
print("Teste: Endpoint /chat com Histórico de Conversa")
print("=" * 70)
print()

# STEP 1: Criar conversa
print("1. Criando/atualizando conversa...")
conv_payload = {
    "user_id": USER_ID,
    "external_contact_id": EXTERNAL_CONTACT,
    "contact_name": "Maria Santos",
    "source": "whatsapp",
    "status": "open"
}

response = requests.post(f"{BASE_URL}/conversations/upsert", json=conv_payload)
if response.status_code == 200:
    conv_data = response.json()
    conversation_id = conv_data['conversation_id']
    print(f"✅ Conversa criada: {conversation_id}")
else:
    print(f"❌ Erro: {response.text}")
    exit(1)

print()

# STEP 2: Adicionar messages ao histórico
print("2. Adicionando messages ao histórico...")

messages = [
    {"direction": "inbound", "type": "user", "text": "Oi, meu nome é Maria"},
    {"direction": "outbound", "type": "assistant", "text": "Olá Maria! Prazer! Como posso ajudar?"},
    {"direction": "inbound", "type": "user", "text": "Quero saber sobre os planos"},
    {"direction": "outbound", "type": "assistant", "text": "Claro! Temos vários planos disponíveis..."},
]

for msg in messages:
    msg_payload = {
        "user_id": USER_ID,
        "external_contact_id": EXTERNAL_CONTACT,
        "direction": msg["direction"],
        "type": msg["type"],
        "text": msg["text"]
    }
    
    response = requests.post(f"{BASE_URL}/messages", json=msg_payload)
    if response.status_code == 200:
        label = "👤 Usuário" if msg["type"] == "user" else "🤖 Assistente"
        print(f"   ✅ {label}: {msg['text'][:40]}...")
    else:
        print(f"   ❌ Erro: {response.text}")

print()

# STEP 3: Testar endpoint /chat COM external_contact_id
print("3. Testando /chat COM external_contact_id (deve lembrar o nome)...")
chat_payload = {
    "user_id": USER_ID,
    "message": "Você sabe meu nome?",
    "external_contact_id": EXTERNAL_CONTACT
}

response = requests.post(f"{BASE_URL}/chat", json=chat_payload)
if response.status_code == 200:
    data = response.json()
    print()
    print("RESPOSTA DO AGENTE:")
    print("-" * 70)
    print(data['reply'])
    print("-" * 70)
    print()
    
    if "Maria" in data['reply'] or "maria" in data['reply']:
        print("✅ SUCESSO! O agente lembrou o nome!")
    else:
        print("⚠️  O agente não mencionou o nome explicitamente")
        print("    (mas pode ter respondido de outra forma)")
else:
    print(f"❌ Erro: {response.text}")

print()

# STEP 4: Testar endpoint /chat SEM external_contact_id
print("4. Testando /chat SEM external_contact_id (não deve lembrar)...")
chat_payload_no_history = {
    "user_id": USER_ID,
    "message": "Você sabe meu nome?"
}

response = requests.post(f"{BASE_URL}/chat", json=chat_payload_no_history)
if response.status_code == 200:
    data = response.json()
    print()
    print("RESPOSTA DO AGENTE (sem histórico):")
    print("-" * 70)
    print(data['reply'])
    print("-" * 70)
    print()
    
    if "Maria" in data['reply'] or "maria" in data['reply']:
        print("⚠️  O agente mencionou o nome sem histórico (inesperado)")
    else:
        print("✅ Correto! Sem external_contact_id, não há histórico")
else:
    print(f"❌ Erro: {response.text}")

print()
print("=" * 70)
print("Teste concluído!")
print("=" * 70)
print()
print("💡 Para o n8n funcionar com memória:")
print("   1. O n8n deve chamar POST /chat com:")
print("      {")
print('        "user_id": "...",')
print('        "message": "...",')
print('        "external_contact_id": "5511999887766"  // número WhatsApp')
print("      }")
print()

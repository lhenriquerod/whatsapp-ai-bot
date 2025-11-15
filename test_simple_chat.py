"""
Teste simples e direto do endpoint /chat
"""
import requests

BASE_URL = "http://localhost:8000"
USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"
EXTERNAL_CONTACT = "5511999887766"

print("=" * 70)
print("Teste: Endpoint /chat com histórico")
print("=" * 70)
print()

payload = {
    "user_id": USER_ID,
    "message": "Você sabe meu nome?",
    "external_contact_id": EXTERNAL_CONTACT
}

print("Enviando requisição...")
print(f"Payload: {payload}")
print()

response = requests.post(f"{BASE_URL}/chat", json=payload)

if response.status_code == 200:
    data = response.json()
    print("RESPOSTA:")
    print("-" * 70)
    print(data['reply'])
    print("-" * 70)
    print()
    
    if "Maria" in data['reply'] or "maria" in data['reply']:
        print("✅ SUCESSO! O agente lembrou o nome!")
    else:
        print("❌ O agente não lembrou o nome")
        print()
        print("💡 Verificando histórico que deveria ter sido enviado...")
        print("   Histórico no banco contém: 'Oi, meu nome é Maria'")
else:
    print(f"❌ Erro {response.status_code}: {response.text}")

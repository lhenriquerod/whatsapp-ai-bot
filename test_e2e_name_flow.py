"""
Teste end-to-end do fluxo de coleta de nome via endpoint /chat
"""
import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "e35af3a4-a7e6-422f-a483-bbcfc9d7c24f"
TEST_CONTACT = "+5511999887766"

print("=" * 60)
print("TESTE END-TO-END: Fluxo de Coleta de Nome")
print("=" * 60)
print()

# Teste 1: Primeira mensagem - deve pedir nome
print("1. Enviando primeira mensagem (novo contato)...")
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "user_id": TEST_USER_ID,
        "message": "Olá!",
        "external_contact_id": TEST_CONTACT
    }
)

print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Resposta: {data['reply'][:100]}...")
    print(f"   Source: {data['source']}")
    
    if "nome" in data['reply'].lower():
        print("   ✅ Perguntou o nome!")
    else:
        print("   ❌ Não perguntou o nome")
else:
    print(f"   ❌ Erro: {response.text}")

print()

# Teste 2: Enviar nome
print("2. Enviando nome...")
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "user_id": TEST_USER_ID,
        "message": "João Silva",
        "external_contact_id": TEST_CONTACT
    }
)

print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Resposta: {data['reply'][:100]}...")
    
    if "joão silva" in data['reply'].lower() and "correto" in data['reply'].lower():
        print("   ✅ Pediu confirmação!")
    else:
        print("   ❌ Não pediu confirmação")
else:
    print(f"   ❌ Erro: {response.text}")

print()

# Teste 3: Confirmar nome
print("3. Confirmando nome...")
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "user_id": TEST_USER_ID,
        "message": "sim",
        "external_contact_id": TEST_CONTACT
    }
)

print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Resposta: {data['reply'][:100]}...")
    
    if "ótimo" in data['reply'].lower():
        print("   ✅ Nome confirmado!")
    else:
        print("   ❌ Confirmação falhou")
else:
    print(f"   ❌ Erro: {response.text}")

print()

# Teste 4: Mensagem normal (deve processar com AI)
print("4. Enviando mensagem normal...")
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "user_id": TEST_USER_ID,
        "message": "Quero saber sobre os produtos",
        "external_contact_id": TEST_CONTACT
    }
)

print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Resposta: {data['reply'][:100]}...")
    print(f"   Source: {data['source']}")
    
    if data['source'] == 'supabase':
        print("   ✅ Processado com AI!")
    else:
        print(f"   ⚠️  Source inesperado: {data['source']}")
else:
    print(f"   ❌ Erro: {response.text}")

print()
print("=" * 60)
print("✅ TESTE END-TO-END CONCLUÍDO!")
print("=" * 60)

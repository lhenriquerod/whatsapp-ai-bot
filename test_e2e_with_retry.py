"""
Teste End-to-End com retry para garantir que o servidor está pronto
"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000"
TEST_USER_ID = "e35af3a4-a7e6-422f-a483-bbcfc9d7c24f"
TEST_PHONE = "+5511999999999"

def wait_for_server(max_attempts=10):
    """Aguarda o servidor estar pronto"""
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print("✅ Servidor está pronto!")
                return True
        except requests.exceptions.ConnectionError:
            print(f"Aguardando servidor... tentativa {i+1}/{max_attempts}")
            time.sleep(1)
    return False

def test_flow():
    print("\n" + "="*60)
    print("TESTE END-TO-END: Fluxo de Coleta de Nome")
    print("="*60 + "\n")
    
    if not wait_for_server():
        print("❌ Servidor não está respondendo!")
        sys.exit(1)
    
    # STEP 1: Primeira mensagem (novo contato)
    print("1. Enviando primeira mensagem (novo contato)...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "Olá!",
            "external_contact_id": TEST_PHONE
        }
    )
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Source: {data.get('source')}")
    print(f"   Resposta: {data['reply'][:100]}...")
    assert "nome" in data['reply'].lower(), "Deveria pedir o nome"
    assert data['source'] == "name_collection", "Source deveria ser name_collection"
    
    time.sleep(1)
    
    # STEP 2: Enviar nome
    print("\n2. Enviando nome...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "Meu nome é João Silva",
            "external_contact_id": TEST_PHONE
        }
    )
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Source: {data.get('source')}")
    print(f"   Resposta: {data['reply'][:100]}...")
    assert "João Silva" in data['reply'], "Deveria confirmar o nome"
    assert data['source'] == "name_collection", "Source deveria ser name_collection"
    
    time.sleep(1)
    
    # STEP 3: Confirmar nome
    print("\n3. Confirmando nome...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "Sim, está correto",
            "external_contact_id": TEST_PHONE
        }
    )
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Source: {data.get('source')}")
    print(f"   Resposta: {data['reply'][:100]}...")
    assert data['source'] == "name_collection", "Source deveria ser name_collection"
    
    time.sleep(1)
    
    # STEP 4: Conversa normal
    print("\n4. Testando conversa normal...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "Como você pode me ajudar?",
            "external_contact_id": TEST_PHONE
        }
    )
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Source: {data.get('source')}")
    print(f"   Resposta: {data['reply'][:100]}...")
    assert data['source'] == "supabase", "Source deveria ser supabase agora"
    
    print("\n" + "="*60)
    print("✅ TESTE COMPLETO! Fluxo de coleta de nome funcionando!")
    print("="*60)

if __name__ == "__main__":
    test_flow()

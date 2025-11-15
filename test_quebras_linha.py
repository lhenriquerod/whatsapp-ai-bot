"""
Teste para verificar se a resposta da API contém quebras de linha
"""
import requests
import json

USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"

print("=" * 70)
print("Teste: Verificando quebras de linha na resposta da API")
print("=" * 70)
print()

# Fazer requisição
print("Enviando requisição para /simulation/chat...")
response = requests.post(
    "http://localhost:8000/simulation/chat",
    json={
        "user_id": USER_ID,
        "message": "Quais os planos disponíveis?"
    },
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
print()

if response.status_code == 200:
    data = response.json()
    reply = data.get("reply", "")
    
    print("RESPOSTA BRUTA (com \\n visível):")
    print("=" * 70)
    print(repr(reply))  # Mostra \n literalmente
    print("=" * 70)
    print()
    
    print("RESPOSTA FORMATADA:")
    print("=" * 70)
    print(reply)
    print("=" * 70)
    print()
    
    # Contar quebras de linha
    num_quebras = reply.count('\n')
    print(f"Número de quebras de linha (\\n): {num_quebras}")
    print()
    
    if num_quebras > 0:
        print("✅ A API está retornando quebras de linha!")
        print("   → O problema pode estar no WhatsApp ou no n8n")
    else:
        print("❌ A API NÃO está retornando quebras de linha!")
        print("   → O problema está no backend (prompt ou AI)")
else:
    print(f"❌ Erro na requisição: {response.text}")

"""
Script para descobrir valores válidos de status testando diretamente
"""
from src.services.supabase_service import _client

print("=" * 60)
print("Testando valores de status através de INSERT direto")
print("=" * 60)

# Lista completa de valores comuns em sistemas similares
test_values = [
    "open", "inativa", "suspensa",  # do campo usuarios.status
    "pendente", "em_andamento", "concluida", "cancelada", "closed",
    "aberta", "fechada", "archived",  # tentativas anteriores
]

for test_status in test_values:
    try:
        test_data = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "external_contact_id": f"test_{test_status}",
            "title": "Test",
            "status": test_status,  # FORÇAR o valor em vez de usar default
        }
        
        result = _client.table("conversations").insert(test_data).execute()
        
        if result.data:
            conv_id = result.data[0]["id"]
            # Sucesso! Vamos limpar
            _client.table("conversations").delete().eq("id", conv_id).execute()
            print(f"✅ '{test_status}' - VÁLIDO")
            
    except Exception as e:
        error_str = str(e)
        if "constraint" in error_str.lower() and "status" in error_str.lower():
            print(f"❌ '{test_status}' - INVÁLIDO (violates status constraint)")
        else:
            # Outro tipo de erro (pode indicar que o valor é válido mas há outro problema)
            print(f"⚠️  '{test_status}' - ERRO: {error_str[:100]}")

print("\n" + "=" * 60)
print("SOLUÇÃO: Remova a constraint ou descubra os valores corretos")
print("=" * 60)

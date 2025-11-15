"""
Script para descobrir valores de status válidos
"""
from src.services.supabase_service import _client

print("=" * 60)
print("Descobrindo valores de status válidos")
print("=" * 60)

# 1. Ver quais valores de status já existem na tabela
try:
    result = _client.table("conversas").select("status").limit(100).execute()
    
    if result.data:
        status_values = set(row.get("status") for row in result.data if row.get("status"))
        print(f"\n✅ Valores de status encontrados em conversas existentes:")
        for status in sorted(status_values):
            print(f"   - '{status}'")
    else:
        print("\n⚠️ Nenhuma conversa encontrada na tabela")
        
except Exception as e:
    print(f"\n❌ Erro ao consultar conversas: {e}")

# 2. Tentar cada valor comum para ver qual funciona
print("\n" + "=" * 60)
print("Testando valores comuns...")
print("=" * 60)

test_values = ["active", "open", "closed", "archived", "pending", "in_progress", "completed", "cancelled"]

for test_status in test_values:
    try:
        # Tentar inserir um registro de teste
        test_data = {
            "user_id": "00000000-0000-0000-0000-000000000001",
            "external_contact_id": f"test_{test_status}",
            "contact_name": "Test",
            "source": "test",
            "status": test_status,
            "titulo": "Test"
        }
        
        result = _client.table("conversas").insert(test_data).execute()
        
        # Se chegou aqui, o valor é válido! Vamos deletar o teste
        if result.data:
            conv_id = result.data[0]["id"]
            _client.table("conversas").delete().eq("id", conv_id).execute()
            print(f"✅ '{test_status}' - VÁLIDO")
        
    except Exception as e:
        error_msg = str(e)
        if "violates check constraint" in error_msg.lower():
            print(f"❌ '{test_status}' - INVÁLIDO (constraint)")
        elif "duplicate key" in error_msg.lower():
            print(f"⚠️ '{test_status}' - JÁ EXISTE (mas é válido)")
        else:
            print(f"❌ '{test_status}' - ERRO: {error_msg[:100]}")

print("\n" + "=" * 60)

"""
Consulta direta para ver a definição da constraint de status
"""
from src.services.supabase_service import _client

# Vamos tentar inserir apenas os campos obrigatórios mínimos
print("Testando insert mínimo sem status...")

try:
    # Tentar sem especificar status (vai usar o default)
    test_data = {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "external_contact_id": "test_default_status",
        "titulo": "Test Default"
    }
    
    result = _client.table("conversas").insert(test_data).execute()
    
    if result.data:
        status_default = result.data[0].get("status")
        conv_id = result.data[0]["id"]
        
        print(f"✅ Insert sem status funcionou!")
        print(f"Status default aplicado: '{status_default}'")
        
        # Limpar
        _client.table("conversas").delete().eq("id", conv_id).execute()
        
        # Agora testar UPDATE com diferentes valores
        print("\nTestando valores através de UPDATE...")
        
        # Criar uma conversa para testar updates
        test_conv = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "external_contact_id": "test_update_status",
            "titulo": "Test Update"
        }
        
        result = _client.table("conversas").insert(test_conv).execute()
        conv_id = result.data[0]["id"]
        
        test_statuses = ["ativa", "inativa", "suspensa", "pendente", "concluida", "cancelada", "em_atendimento", "finalizada"]
        
        for test_status in test_statuses:
            try:
                _client.table("conversas").update({"status": test_status}).eq("id", conv_id).execute()
                print(f"✅ '{test_status}' - VÁLIDO")
            except Exception as e:
                if "constraint" in str(e).lower():
                    print(f"❌ '{test_status}' - INVÁLIDO (constraint)")
                else:
                    print(f"❌ '{test_status}' - ERRO: {str(e)[:80]}")
        
        # Limpar
        _client.table("conversas").delete().eq("id", conv_id).execute()
        
except Exception as e:
    print(f"❌ Erro: {e}")
    
    # Extrair informação do erro
    error_str = str(e)
    if "default" in error_str.lower() or "null" in error_str.lower():
        print("\n💡 O campo status pode ser obrigatório (NOT NULL sem default válido)")

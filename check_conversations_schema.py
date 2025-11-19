"""
Check the actual schema of conversations table
"""
from src.services.supabase_service import _client

print("=" * 60)
print("Verificando schema da tabela conversations")
print("=" * 60)

# Try to get any existing record or describe the table
try:
    # Try to select all columns from the table (limit 1)
    result = _client.table("conversations").select("*").limit(1).execute()
    
    if result.data and len(result.data) > 0:
        print("\n✅ Colunas encontradas na tabela (via registro existente):")
        for column in result.data[0].keys():
            print(f"   - {column}")
    else:
        print("\n⚠️ Tabela existe mas está vazia")
        print("\nTentando inserir registro de teste para descobrir colunas válidas...")
        
        # Try minimal insert to see what columns are required/valid
        test_data = {
            "user_id": "00000000-0000-0000-0000-000000000001",
            "external_contact_id": "test_schema_check",
            "source": "test",
            "status": "open"
        }
        
        try:
            insert_result = _client.table("conversations").insert(test_data).execute()
            if insert_result.data:
                print("\n✅ Registro de teste inserido com sucesso!")
                print("✅ Colunas da tabela:")
                for column in insert_result.data[0].keys():
                    print(f"   - {column}")
                
                # Delete the test record
                conv_id = insert_result.data[0]["id"]
                _client.table("conversations").delete().eq("id", conv_id).execute()
                print("\n✅ Registro de teste removido")
        except Exception as insert_error:
            print(f"\n❌ Erro ao inserir teste: {insert_error}")
        
except Exception as e:
    print(f"\n❌ Erro ao verificar schema: {e}")

print("\n" + "=" * 60)

"""
Script para verificar constraints da tabela conversas
"""
from src.services.supabase_service import _client

print("=" * 60)
print("Consultando constraints da tabela conversas")
print("=" * 60)

# Query para ver todas as constraints CHECK da tabela conversas
query = """
SELECT 
    con.conname AS constraint_name,
    pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
WHERE rel.relname = 'conversas'
    AND con.contype = 'c'
ORDER BY con.conname;
"""

try:
    result = _client.rpc('exec_sql', {'query': query}).execute()
    print("\n✅ Constraints CHECK encontradas:")
    print(result.data)
except Exception as e:
    print(f"\n❌ Erro ao consultar constraints: {e}")
    print("\nTentando consulta alternativa...")
    
    # Alternativa: Consultar através do information_schema
    try:
        # Vamos tentar inserir um valor inválido e capturar o erro
        test_data = {
            "user_id": "00000000-0000-0000-0000-000000000001",
            "external_contact_id": "test_constraint_check",
            "contact_name": "Test",
            "source": "test",
            "status": "INVALID_STATUS_TO_CHECK_CONSTRAINT"  # Valor inválido para provocar erro
        }
        
        _client.table("conversas").insert(test_data).execute()
        print("Nenhuma constraint encontrada - qualquer valor é aceito")
        
    except Exception as e2:
        error_msg = str(e2)
        print(f"\n📋 Erro capturado ao tentar inserir valor inválido:")
        print(error_msg)
        
        # Tentar extrair valores permitidos do erro
        if "violates check constraint" in error_msg.lower():
            print("\n✅ Constraint CHECK ativa!")
            print("Analise o erro acima para ver os valores permitidos")

print("\n" + "=" * 60)
print("Verificação concluída")
print("=" * 60)

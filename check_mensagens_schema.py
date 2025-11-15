"""
Script para descobrir a estrutura real da tabela mensagens no Supabase
"""
import sys
sys.path.insert(0, '.')

from src.services.supabase_service import _client

print("Consultando estrutura da tabela 'mensagens'...")
print("=" * 70)

try:
    # Tentar buscar 1 registro para ver os campos
    result = _client.table("mensagens").select("*").limit(1).execute()
    
    if result.data and len(result.data) > 0:
        print("Campos encontrados:")
        for key in result.data[0].keys():
            print(f"  - {key}")
    else:
        print("Tabela vazia. Vou tentar consultar o schema...")
        
        # Alternativa: tentar inserir e ver o erro
        print("\nTentando inserir para descobrir campos obrigatórios...")
        try:
            _client.table("mensagens").insert({}).execute()
        except Exception as e:
            print(f"Erro (esperado): {e}")
            
except Exception as e:
    print(f"Erro: {e}")

print("=" * 70)

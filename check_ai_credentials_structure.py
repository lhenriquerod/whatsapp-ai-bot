"""
Script para verificar estrutura completa da tabela ai_credentials
"""
import sys
sys.path.insert(0, '.')

from src.services.supabase_service import _client

print("=" * 70)
print("Estrutura da tabela ai_credentials")
print("=" * 70)
print()

try:
    # Buscar um registro para ver a estrutura
    result = _client.table("ai_credentials").select("*").limit(1).execute()
    
    if result.data:
        print("✅ Registro encontrado!")
        print()
        print("Campos e valores:")
        for key, value in result.data[0].items():
            # Mascarar api_key se existir
            if 'api_key' in key.lower() and value:
                value = f"{value[:10]}...{value[-4:]}" if len(str(value)) > 14 else "***"
            print(f"  - {key}: {value}")
    else:
        print("⚠️  Tabela vazia")
        print()
        print("Tentando inserir um registro de teste para ver campos obrigatórios...")
        try:
            _client.table("ai_credentials").insert({}).execute()
        except Exception as e:
            print(f"Erro (esperado): {e}")
            
except Exception as e:
    print(f"❌ Erro: {e}")

print()
print("=" * 70)

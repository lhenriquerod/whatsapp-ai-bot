"""
Script para verificar se existe tabela de credenciais de IA
"""
import sys
sys.path.insert(0, '.')

from src.services.supabase_service import _client

print("=" * 70)
print("Verificando tabelas relacionadas a credenciais de IA")
print("=" * 70)
print()

# Tentar acessar possíveis nomes de tabelas
possible_tables = [
    "ai_credentials",
    "user_credentials",
    "api_credentials",
    "user_ai_config",
    "ai_config"
]

existing_tables = []

for table_name in possible_tables:
    try:
        result = _client.table(table_name).select("*").limit(1).execute()
        print(f"✅ Tabela '{table_name}' EXISTE!")
        existing_tables.append(table_name)
        
        # Mostrar estrutura
        if result.data:
            print(f"   Campos: {', '.join(result.data[0].keys())}")
        else:
            print(f"   Tabela vazia, não foi possível determinar campos")
        print()
    except Exception as e:
        if "not found" in str(e).lower() or "does not exist" in str(e).lower():
            print(f"❌ Tabela '{table_name}' não existe")
        else:
            print(f"⚠️  Erro ao verificar '{table_name}': {e}")
        print()

print("=" * 70)
if existing_tables:
    print(f"Tabelas encontradas: {', '.join(existing_tables)}")
else:
    print("❌ Nenhuma tabela de credenciais de IA encontrada")
    print()
    print("💡 Será necessário criar uma tabela para armazenar as credenciais dos usuários.")
    print()
    print("Estrutura sugerida:")
    print("""
    CREATE TABLE ai_credentials (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
        provider VARCHAR(50) NOT NULL CHECK (provider IN ('openai', 'anthropic', 'google', 'cohere')),
        api_key TEXT NOT NULL,
        model VARCHAR(100),
        temperature DECIMAL(3,2) DEFAULT 0.2,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """)
print("=" * 70)

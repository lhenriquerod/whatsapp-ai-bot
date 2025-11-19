"""
Check for foreign key constraints referencing old table names
"""
from src.services.supabase_service import _client

print("=" * 60)
print("Verificando constraints do banco de dados")
print("=" * 60)

# Check if usuarios table exists
print("\n1. Verificando se tabela 'usuarios' existe:")
try:
    result = _client.table("usuarios").select("id").limit(1).execute()
    print("   ✅ Tabela 'usuarios' EXISTE (problema!)")
except Exception as e:
    if "does not exist" in str(e) or "42P01" in str(e):
        print("   ✅ Tabela 'usuarios' NÃO existe (correto)")
    else:
        print(f"   ❌ Erro: {e}")

# Check if users table exists
print("\n2. Verificando se tabela 'users' existe:")
try:
    result = _client.table("users").select("id").limit(1).execute()
    print(f"   ✅ Tabela 'users' existe e tem {len(result.data)} registros")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Check if conversas table exists
print("\n3. Verificando se tabela 'conversas' existe:")
try:
    result = _client.table("conversas").select("id").limit(1).execute()
    print("   ⚠️ Tabela 'conversas' EXISTE (deveria ser 'conversations')")
except Exception as e:
    if "does not exist" in str(e) or "PGRST205" in str(e):
        print("   ✅ Tabela 'conversas' NÃO existe (correto)")
    else:
        print(f"   ❌ Erro: {e}")

# Check if conversations table exists
print("\n4. Verificando se tabela 'conversations' existe:")
try:
    result = _client.table("conversations").select("id").limit(1).execute()
    print(f"   ✅ Tabela 'conversations' existe e tem {len(result.data)} registros")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "=" * 60)
print("DIAGNÓSTICO:")
print("=" * 60)
print("""
O erro 'relation "usuarios" does not exist' indica que:

1. A tabela 'conversations' existe
2. Mas ela tem um FOREIGN KEY que referencia 'usuarios'
3. A tabela 'usuarios' foi renomeada para 'users'
4. Precisamos DROPAR o FK antigo e criar um novo apontando para 'users'

Você precisa executar no SQL Editor do Supabase:

-- Dropar constraint antigo
ALTER TABLE conversations 
DROP CONSTRAINT IF EXISTS conversations_user_id_fkey;

-- Criar novo constraint apontando para 'users'
ALTER TABLE conversations
ADD CONSTRAINT conversations_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Fazer o mesmo para 'messages' se necessário
ALTER TABLE messages
DROP CONSTRAINT IF EXISTS messages_user_id_fkey;

ALTER TABLE messages
ADD CONSTRAINT messages_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
""")
print("=" * 60)

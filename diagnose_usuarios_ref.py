"""
Script para diagnosticar referências à tabela usuarios no banco
"""
import sys
sys.path.insert(0, '.')

from src.services.supabase_service import _client

print("=" * 70)
print("Diagnosticando referências à tabela 'usuarios' no banco")
print("=" * 70)
print()

# Tentar fazer um upsert simples para ver o erro completo
print("1. Tentando criar uma conversa para ver o erro...")
try:
    test_data = {
        "user_id": "e35af3a4-a7e6-422f-a483-bbcfc9d7c24f",
        "external_contact_id": "test_diagnostic",
        "title": "Test"
    }
    
    result = _client.table("conversations").insert(test_data).execute()
    print("✅ Insert funcionou! Nenhum erro relacionado a 'usuarios'")
    
    # Limpar
    if result.data:
        _client.table("conversations").delete().eq("id", result.data[0]['id']).execute()
        
except Exception as e:
    error_msg = str(e)
    print(f"❌ Erro encontrado:")
    print(f"   {error_msg}")
    print()
    
    if "usuarios" in error_msg.lower():
        print("⚠️  CONFIRMADO: O erro menciona a tabela 'usuarios'")
        print()
        print("💡 SOLUÇÃO:")
        print("   Execute o script SQL fix_usuarios_references.sql no Supabase")
        print("   Ou execute manualmente:")
        print()
        print("   ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversas_user_id_fkey;")
        print("   ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversations_user_id_fkey;")
        print("   ALTER TABLE conversations")
        print("   ADD CONSTRAINT conversations_user_id_fkey")
        print("   FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;")
    else:
        print("ℹ️  Erro não relacionado a 'usuarios'")

print()
print("=" * 70)

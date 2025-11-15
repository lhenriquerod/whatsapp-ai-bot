"""
Script simples para testar get_context() com dados existentes
"""
from src.services.supabase_service import get_context

# User ID válido (do list_users.py)
USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"

print("=" * 60)
print("Testando get_context()")
print("=" * 60)

print(f"\nBuscando contexto para user_id: {USER_ID}")
print("-" * 60)

try:
    context = get_context(owner_id=USER_ID)
    
    print("\n📋 Contexto retornado:")
    print(context)
    print("\n" + "-" * 60)
    
    # Estatísticas
    linhas = context.split("\n")
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de linhas: {len(linhas)}")
    print(f"   - Tamanho: {len(context)} caracteres")
    
    # Verificar se há contexto real ou mensagem padrão
    if "Nenhuma base de conhecimento" in context:
        print("\n⚠️  Nenhum registro encontrado na base de conhecimento")
        print("   Execute 'python test_knowledge_base.py' para inserir dados de exemplo")
    else:
        print("\n✅ Contexto carregado com sucesso!")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

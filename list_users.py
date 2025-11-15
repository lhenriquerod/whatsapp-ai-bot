"""
Script para listar users existentes ou criar um user de teste
"""
from src.services.supabase_service import _client

print("=" * 60)
print("Consultando usuários existentes...")
print("=" * 60)

try:
    # Listar usuários da tabela usuarios (campos do RELATORIO_ESTRUTURA_BD.md)
    result = _client.table("usuarios").select("id, nome, telefone, plano, status").limit(5).execute()
    
    if result.data and len(result.data) > 0:
        print(f"\n✅ Encontrados {len(result.data)} usuários:")
        for user in result.data:
            print(f"   - ID: {user['id']}")
            print(f"     Nome: {user.get('nome', 'N/A')}")
            print(f"     Telefone: {user.get('telefone', 'N/A')}")
            print(f"     Plano: {user.get('plano', 'N/A')}")
            print()
        
        # Usar o primeiro usuário para teste
        first_user_id = result.data[0]['id']
        print(f"💡 Use este user_id para testes: {first_user_id}")
        
    else:
        print("\n⚠️ Nenhum usuário encontrado na tabela 'usuarios'")
        print("\nVocê precisa:")
        print("1. Criar um usuário através do Supabase Auth (signup)")
        print("2. Ou criar diretamente na tabela usuarios (se permitido)")
        
except Exception as e:
    print(f"\n❌ Erro ao consultar usuários: {e}")
    print("\nTentando consultar auth.users...")
    
    try:
        # Algumas instalações podem ter acesso direto ao auth.users
        result = _client.rpc('get_auth_users').execute()
        print(result.data)
    except:
        print("❌ Não foi possível acessar auth.users diretamente")
        print("\n💡 Solução: Crie um usuário através do Supabase Dashboard")
        print("   Authentication → Users → Add user")

print("\n" + "=" * 60)

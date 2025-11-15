"""
Analisa a relação entre mensagens e conversas para descobrir o nome do contato
"""
import sys
sys.path.insert(0, '.')

from src.services.supabase_service import _client

print("=" * 70)
print("ANÁLISE: Relação entre mensagens e conversas")
print("=" * 70)
print()

# Buscar uma mensagem de exemplo
print("1. Buscando mensagens recentes...")
msgs = _client.table("mensagens").select("*").order("created_at", desc=True).limit(3).execute()

if msgs.data:
    for msg in msgs.data:
        print(f"\nMensagem ID: {msg['id']}")
        print(f"  conversa_id: {msg.get('conversa_id', 'N/A')}")
        print(f"  user_id: {msg.get('user_id', 'N/A')}")
        print(f"  external_contact_id: {msg.get('external_contact_id', 'N/A')}")
        print(f"  tipo: {msg.get('tipo', 'N/A')}")
        print(f"  mensagem: {msg.get('mensagem', 'N/A')[:50]}...")
        
        # Buscar a conversa relacionada
        conversa_id = msg.get('conversa_id')
        if conversa_id:
            conv = _client.table("conversas").select("*").eq("id", conversa_id).execute()
            if conv.data:
                c = conv.data[0]
                print(f"\n  → Conversa relacionada:")
                print(f"     contact_name: {c.get('contact_name', 'N/A')}")
                print(f"     user_id: {c.get('user_id', 'N/A')}")
                print(f"     external_contact_id: {c.get('external_contact_id', 'N/A')}")
                print(f"     source/canal: {c.get('source', c.get('canal', 'N/A'))}")
else:
    print("Nenhuma mensagem encontrada")

print()
print("=" * 70)
print("2. Verificando schema das tabelas")
print("=" * 70)
print()

# Pegar 1 conversa pra ver os campos
conv = _client.table("conversas").select("*").limit(1).execute()
if conv.data:
    print("Campos da tabela CONVERSAS:")
    for key in conv.data[0].keys():
        print(f"  - {key}")

print()

# Pegar 1 mensagem pra ver os campos  
msg = _client.table("mensagens").select("*").limit(1).execute()
if msg.data:
    print("Campos da tabela MENSAGENS:")
    for key in msg.data[0].keys():
        print(f"  - {key}")

print()
print("=" * 70)
print("CONCLUSÃO")
print("=" * 70)
print()
print("Para saber o nome do contato:")
print("1. Mensagem tem 'conversa_id' ou 'user_id + external_contact_id'")
print("2. Usar esses campos para buscar na tabela 'conversas'")
print("3. O campo 'contact_name' da conversa tem o nome da pessoa")

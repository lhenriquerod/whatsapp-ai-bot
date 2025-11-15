"""
Verifica constraint do campo tipo na tabela mensagens
"""
import sys
sys.path.insert(0, '.')

from src.services.supabase_service import _client

print("Tentando descobrir valores permitidos para 'tipo'...")
print("=" * 70)

# Tentar inserir valores diferentes para ver qual funciona
test_values = ["text", "TEXT", "user", "assistant", "incoming", "outgoing", "message"]

for val in test_values:
    try:
        result = _client.table("mensagens").insert({
            "conversa_id": "00000000-0000-0000-0000-000000000000",  # UUID inválido só pra testar
            "tipo": val,
            "mensagem": "teste",
            "direction": "incoming"
        }).execute()
        print(f"✅ '{val}' - ACEITO (mas falhou por outro motivo provavelmente)")
    except Exception as e:
        error_msg = str(e)
        if "mensagens_tipo_check" in error_msg:
            print(f"❌ '{val}' - REJEITADO pelo constraint")
        elif "violates foreign key" in error_msg or "conversa_id" in error_msg:
            print(f"✅ '{val}' - ACEITO (falhou apenas pela FK)")
        else:
            print(f"⚠️  '{val}' - Erro: {error_msg[:80]}")

print("=" * 70)
print("\n💡 Vou buscar uma mensagem existente para ver o valor real...")

try:
    result = _client.table("mensagens").select("tipo, mensagem, direction").limit(5).execute()
    if result.data:
        print("\nExemplos de mensagens existentes:")
        for msg in result.data:
            print(f"  tipo='{msg.get('tipo')}' | direction='{msg.get('direction')}' | msg='{msg.get('mensagem', '')[:30]}'")
    else:
        print("Nenhuma mensagem existente encontrada")
except Exception as e:
    print(f"Erro: {e}")

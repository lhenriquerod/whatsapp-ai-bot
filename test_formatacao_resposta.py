"""
Teste de formatação de resposta do assistente
"""
import sys
sys.path.insert(0, '.')

from src.services.personality_service import (
    get_agent_personality,
    build_system_prompt_with_personality
)
from src.services.supabase_service import get_context

USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"

print("=" * 70)
print("Teste de Formatação de Resposta")
print("=" * 70)
print()

# Buscar personalidade e contexto
personality = get_agent_personality(USER_ID)
kb_context = get_context(USER_ID)

# Montar prompt completo
system_prompt = build_system_prompt_with_personality(kb_context, personality)

print("SYSTEM PROMPT COMPLETO:")
print("=" * 70)
print(system_prompt)
print("=" * 70)
print()

print("✅ Instruções de formatação adicionadas!")
print()
print("Agora teste via API:")
print()
print(f'curl -X POST http://localhost:8000/simulation/chat \\')
print(f'  -H "Content-Type: application/json" \\')
print(f'  -d \'{{"user_id": "{USER_ID}", "message": "Quais os produtos disponíveis?"}}\'')
print()
print("A resposta deve vir melhor formatada com:")
print("  - Quebras de linha claras")
print("  - Negrito nos títulos (*texto*)")
print("  - Emojis opcionais (💰, 👥, ✨, etc)")
print("  - Listas com marcadores")
print()

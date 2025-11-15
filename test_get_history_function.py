"""
Testa diretamente a função get_conversation_history
"""
import sys
sys.path.insert(0, '.')

from src.services.message_service import get_conversation_history

USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"
EXTERNAL_CONTACT = "5511999887766"

print("Testando get_conversation_history()...")
print("-" * 70)

history = get_conversation_history(USER_ID, EXTERNAL_CONTACT, limit=10)

print(f"Mensagens retornadas: {len(history)}")
print()

if history:
    for msg in history:
        print(f"Campos no dicionário: {list(msg.keys())}")
        print(f"  direction: {msg.get('direction')}")
        print(f"  mensagem: {msg.get('mensagem', 'N/A')[:50]}")
        print(f"  timestamp: {msg.get('timestamp', 'N/A')}")
        print()
else:
    print("❌ Nenhuma mensagem retornada!")

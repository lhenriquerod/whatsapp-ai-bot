"""
Verifica se as mensagens do teste foram salvas corretamente
"""
import sys
sys.path.insert(0, '.')

from src.services.supabase_service import _client

EXTERNAL_CONTACT = "5511999887766"
USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"

print("Buscando conversa...")
conv = _client.table("conversas").select("id").eq("user_id", USER_ID).eq("external_contact_id", EXTERNAL_CONTACT).execute()

if conv.data:
    conversation_id = conv.data[0]['id']
    print(f"✅ Conversa encontrada: {conversation_id}")
    print()
    
    print("Mensagens na conversa:")
    print("-" * 70)
    
    msgs = _client.table("mensagens").select("*").eq("conversa_id", conversation_id).order("created_at").execute()
    
    if msgs.data:
        for msg in msgs.data:
            direction = msg.get('direction', 'N/A')
            tipo = msg.get('tipo', 'N/A')
            mensagem = msg.get('mensagem', 'N/A')
            user_id = msg.get('user_id', 'N/A')
            
            emoji = "👤" if direction == "inbound" else "🤖"
            print(f"{emoji} [{tipo}] [{direction}] user_id={user_id[-4:] if user_id != 'N/A' else 'N/A'}")
            print(f"   {mensagem[:60]}")
            print()
    else:
        print("❌ Nenhuma mensagem encontrada!")
else:
    print("❌ Conversa não encontrada!")

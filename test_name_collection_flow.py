"""
Teste do fluxo de coleta de nome
Valida todo o processo: boas-vindas → coleta → confirmação → salvamento
"""
from src.services.name_collection_service import process_name_collection_flow, get_welcome_message
from src.services.state_manager import ConversationState, get_conversation_state
from src.services.supabase_service import _client

# Configurações
TEST_PHONE = "+5511999887766"
TEST_USER_ID = "e35af3a4-a7e6-422f-a483-bbcfc9d7c24f"  # User ID real do Supabase

print("=" * 60)
print("TESTE: FLUXO DE COLETA DE NOME")
print("=" * 60)
print()

# Limpar dados de teste anteriores
print("1. Limpando dados de teste anteriores...")
try:
    _client.table("conversations").delete().eq("external_contact_id", TEST_PHONE).execute()
    print("   ✅ Dados limpos")
except Exception as e:
    print(f"   ⚠️  Erro ao limpar (pode ser normal): {e}")

print()

# Teste 1: Primeira interação - deve pedir nome
print("2. Testando primeira interação (novo contato)...")
response, should_continue = process_name_collection_flow(
    message_text="Olá!",
    external_contact_id=TEST_PHONE,
    user_id=TEST_USER_ID
)

print(f"   Resposta: {response}")
print(f"   Processar com AI? {should_continue}")

if "qual é o seu nome" in response.lower():
    print("   ✅ Perguntou o nome corretamente")
else:
    print("   ❌ Não perguntou o nome!")

# Buscar estado da conversa
conv = _client.table("conversations").select("id, conversation_state").eq("external_contact_id", TEST_PHONE).single().execute()
conversation_id = conv.data['id']
state = conv.data['conversation_state']

print(f"   Estado atual: {state}")
if state == ConversationState.AWAITING_NAME:
    print("   ✅ Estado correto: AWAITING_NAME")
else:
    print(f"   ❌ Estado incorreto: {state}")

print()

# Teste 2: Enviar nome
print("3. Testando envio de nome...")
response, should_continue = process_name_collection_flow(
    message_text="João Silva",
    external_contact_id=TEST_PHONE,
    user_id=TEST_USER_ID
)

print(f"   Resposta: {response}")
print(f"   Processar com AI? {should_continue}")

if "joão silva" in response.lower() and "está correto" in response.lower():
    print("   ✅ Pediu confirmação corretamente")
else:
    print("   ❌ Não pediu confirmação!")

# Verificar estado
state = get_conversation_state(conversation_id)
print(f"   Estado atual: {state}")
if state == ConversationState.CONFIRMING_NAME:
    print("   ✅ Estado correto: CONFIRMING_NAME")
else:
    print(f"   ❌ Estado incorreto: {state}")

print()

# Teste 3: Confirmar nome
print("4. Testando confirmação positiva...")
response, should_continue = process_name_collection_flow(
    message_text="sim",
    external_contact_id=TEST_PHONE,
    user_id=TEST_USER_ID
)

print(f"   Resposta: {response}")
print(f"   Processar com AI? {should_continue}")

if "ótimo" in response.lower() and "como posso te ajudar" in response.lower():
    print("   ✅ Confirmou e liberou para conversa")
else:
    print("   ❌ Resposta incorreta!")

# Verificar estado e nome salvo
conv = _client.table("conversations").select("conversation_state, contact_name").eq("id", conversation_id).single().execute()
state = conv.data['conversation_state']
name = conv.data['contact_name']

print(f"   Estado atual: {state}")
print(f"   Nome salvo: {name}")

if state == ConversationState.ACTIVE:
    print("   ✅ Estado correto: ACTIVE")
else:
    print(f"   ❌ Estado incorreto: {state}")

if name == "João Silva":
    print("   ✅ Nome salvo corretamente")
else:
    print(f"   ❌ Nome incorreto: {name}")

print()

# Teste 4: Mensagem normal após nome salvo
print("5. Testando mensagem normal (nome já salvo)...")
response, should_continue = process_name_collection_flow(
    message_text="Quero saber sobre os produtos",
    external_contact_id=TEST_PHONE,
    user_id=TEST_USER_ID
)

print(f"   Resposta: '{response}'")
print(f"   Processar com AI? {should_continue}")

if response == "" and should_continue == True:
    print("   ✅ Passou para o AI processar")
else:
    print("   ❌ Não passou para o AI!")

print()
print("=" * 60)
print("TESTE DE NEGAÇÃO")
print("=" * 60)
print()

# Limpar e testar fluxo de negação
TEST_PHONE_2 = "+5511988776655"

print("6. Limpando dados para teste de negação...")
_client.table("conversations").delete().eq("external_contact_id", TEST_PHONE_2).execute()

print("7. Criando nova conversa...")
process_name_collection_flow("Oi", TEST_PHONE_2, TEST_USER_ID)

print("8. Enviando nome...")
process_name_collection_flow("Maria Souza", TEST_PHONE_2, TEST_USER_ID)

print("9. Negando confirmação...")
response, should_continue = process_name_collection_flow(
    message_text="não",
    external_contact_id=TEST_PHONE_2,
    user_id=TEST_USER_ID
)

print(f"   Resposta: {response}")

if "nome correto" in response.lower():
    print("   ✅ Pediu nome novamente")
else:
    print("   ❌ Não pediu nome novamente!")

# Verificar estado
conv2 = _client.table("conversations").select("id, conversation_state").eq("external_contact_id", TEST_PHONE_2).single().execute()
state = conv2.data['conversation_state']

if state == ConversationState.AWAITING_NAME:
    print("   ✅ Voltou para AWAITING_NAME")
else:
    print(f"   ❌ Estado incorreto: {state}")

print()
print("=" * 60)
print("✅ TODOS OS TESTES CONCLUÍDOS!")
print("=" * 60)

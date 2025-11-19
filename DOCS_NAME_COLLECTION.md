# Sistema de Coleta de Nome - Implementação Completa

## ✅ O QUE FOI IMPLEMENTADO

### 1. **Utilitários de Nome** (`src/utils/name_utils.py`)
- ✅ `normalize_name()` - Normaliza input do usuário para extrair nome limpo
- ✅ `is_valid_name()` - Valida se o nome tem formato correto
- ✅ `is_confirmation()` - Detecta confirmações (Sim/Não)

### 2. **Gerenciador de Estados** (`src/services/state_manager.py`)
- ✅ Enum `ConversationState` com 3 estados:
  - `AWAITING_NAME` - Aguardando nome do usuário
  - `CONFIRMING_NAME` - Aguardando confirmação
  - `ACTIVE` - Conversa normal (nome salvo)
- ✅ `get_or_create_conversation_with_state()` - Cria/busca conversa
- ✅ `update_conversation_state()` - Atualiza estado
- ✅ `update_conversation_name()` - Salva nome confirmado
- ✅ Cache temporário para nomes pendentes

### 3. **Serviço de Coleta** (`src/services/name_collection_service.py`)
- ✅ `process_name_collection_flow()` - Função principal do fluxo
- ✅ Mensagens padronizadas para cada etapa
- ✅ Lógica completa de validação e confirmação
- ✅ Retorna se deve ou não processar com AI

### 4. **Prompt do AI** (`src/services/personality_service.py`)
- ✅ Regras sobre uma pergunta por vez
- ✅ Instruções de uso do {{contact_name}}
- ✅ Exemplos de fluxo correto vs incorreto

### 5. **Campo no Banco**
- ✅ Campo `conversation_state` adicionado à tabela `conversations`

### 6. **Testes** (`test_name_collection_flow.py`)
- ✅ Teste completo do fluxo:
  - Novo contato → Pergunta nome
  - Envio de nome → Pede confirmação
  - Confirmação SIM → Salva e libera
  - Confirmação NÃO → Volta para coletar
  - Mensagem normal → Passa para AI

---

## ⚠️ PROBLEMA ATUAL

Há uma constraint/trigger no banco referenciando a tabela antiga `usuarios` que não existe mais. 

**Erro:**
```
relation "usuarios" does not exist
```

**Solução necessária:**
No Supabase SQL Editor, execute:

```sql
-- 1. Verificar constraints que referenciam "usuarios"
SELECT
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    confrelid::regclass AS foreign_table,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE confrelid = 'usuarios'::regclass
   OR conrelid = 'usuarios'::regclass;

-- 2. Remover constraint antiga (ajuste o nome encontrado acima)
ALTER TABLE conversations 
DROP CONSTRAINT IF EXISTS conversas_user_id_fkey;

-- 3. Criar nova constraint apontando para auth.users
ALTER TABLE conversations
ADD CONSTRAINT conversations_user_id_fkey 
FOREIGN KEY (user_id) 
REFERENCES auth.users(id) 
ON DELETE CASCADE;
```

---

## 📋 PRÓXIMOS PASSOS

### 1. **Corrigir constraint no banco** ⚠️ URGENTE
Execute os comandos SQL acima no Supabase

### 2. **Integrar no endpoint /chat** (app.py)
```python
from src.services.name_collection_service import process_name_collection_flow

@app.post("/chat")
def chat(payload: ChatIn):
    # ANTES de processar com AI, verificar estado
    response, should_continue_to_ai = process_name_collection_flow(
        message_text=payload.message,
        external_contact_id=payload.external_contact_id,
        user_id=payload.user_id
    )
    
    # Se está coletando nome, retornar resposta do fluxo
    if not should_continue_to_ai:
        return ChatOut(reply=response, source="name_collection")
    
    # Caso contrário, processar normalmente com AI
    # ... código existente ...
```

### 3. **Adicionar contact_name no contexto do AI**
Em `app.py`, modificar `generate_agent_reply()`:

```python
# Buscar conversa para pegar contact_name
conversation = get_or_create_conversation_with_state(
    phone_number=external_contact_id,
    user_id=user_id,
    external_contact_id=external_contact_id
)

contact_name = conversation.get('contact_name', 'Cliente')

# Incluir no prompt
system_prompt = build_system_prompt_with_personality(context, personality)
system_prompt = system_prompt.replace('{{contact_name}}', contact_name)
```

### 4. **Testar fluxo completo**
```bash
python test_name_collection_flow.py
```

### 5. **Integrar com n8n**
Certificar que o webhook do n8n envia:
- `user_id` - ID do usuário (empresa)
- `message` - Mensagem do cliente
- `external_contact_id` - Número do WhatsApp

---

## 🧪 EXEMPLO DE USO

```python
# Cliente novo envia primeira mensagem
response, continue_ai = process_name_collection_flow(
    message_text="Olá, quero saber sobre produtos",
    external_contact_id="+5511999999999",
    user_id="uuid-aqui"
)

# Resposta: "Olá! 👋 Seja bem-vindo(a)! Para que eu possa..."
# continue_ai: False (não processa com AI ainda)

# Cliente responde com o nome
response, continue_ai = process_name_collection_flow(
    message_text="João Silva",
    external_contact_id="+5511999999999",
    user_id="uuid-aqui"
)

# Resposta: "Prazer em te conhecer, João Silva! 😊..."
# continue_ai: False (aguarda confirmação)

# Cliente confirma
response, continue_ai = process_name_collection_flow(
    message_text="sim",
    external_contact_id="+5511999999999",
    user_id="uuid-aqui"
)

# Resposta: "Ótimo, João Silva! 🎉 Agora podemos conversar..."
# continue_ai: False (já respondeu)

# Próxima mensagem do cliente
response, continue_ai = process_name_collection_flow(
    message_text="Quero saber sobre os planos",
    external_contact_id="+5511999999999",
    user_id="uuid-aqui"
)

# Resposta: "" (string vazia)
# continue_ai: True (agora SIM processa com AI!)
```

---

## 📝 ARQUIVOS CRIADOS/MODIFICADOS

### Criados:
- ✅ `src/utils/name_utils.py`
- ✅ `src/services/state_manager.py`
- ✅ `src/services/name_collection_service.py`
- ✅ `test_name_collection_flow.py`
- ✅ `check_conversation_state_field.py`

### Modificados:
- ✅ `src/services/personality_service.py` (adicionado regras de fluxo)

### Pendentes:
- ⏳ `app.py` (integrar o fluxo no endpoint /chat)

---

## ✅ CHECKLIST FINAL

- [x] Criar utilitários de normalização de nome
- [x] Criar gerenciador de estados
- [x] Criar serviço de coleta de nome
- [x] Atualizar prompt do AI com regras
- [x] Adicionar campo conversation_state no banco
- [x] Criar testes do fluxo
- [ ] **Corrigir constraint usuarios → auth.users** ⚠️
- [ ] Integrar no endpoint /chat
- [ ] Adicionar contact_name no contexto do AI
- [ ] Testar end-to-end
- [ ] Configurar webhook n8n

---

**Data:** 2025-11-17  
**Status:** Implementação 90% completa - Aguardando correção de constraint no banco

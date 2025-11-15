# 📋 Documentação das Novas Rotas - Conversas e Mensagens

## 🎯 Resumo

Implementação de duas rotas HTTP REST para registrar conversas e mensagens vindas do WhatsApp através do n8n.

---

## 📂 Arquivos Criados/Modificados

### ✅ Novos Arquivos:

1. **`src/models/conversation.py`** - Models Pydantic para conversas
2. **`src/models/message.py`** - Models Pydantic para mensagens
3. **`src/services/conversation_service.py`** - Lógica de negócio para conversas
4. **`src/services/message_service.py`** - Lógica de negócio para mensagens
5. **`test_conversation_api.py`** - Script de testes

### 🔧 Arquivos Modificados:

1. **`app.py`** - Adicionadas as rotas `/conversations/upsert` e `/messages`
2. **`requirements.txt`** - Adicionado `requests` para testes

---

## 🔌 Endpoints Implementados

### 1. `POST /conversations/upsert`

**Descrição:** Garante que existe uma conversa para um par `(user_id, external_contact_id)`.

**Request:**
```json
{
  "user_id": "uuid-string",
  "external_contact_id": "5511999887766",
  "contact_name": "João Silva",
  "source": "whatsapp",
  "status": "open",
  "started_at_ts": 1699999999
}
```

**Response (200 OK):**
```json
{
  "conversation_id": "uuid-da-conversa",
  "created": true
}
```

**Lógica:**
- Se conversa **não existe**: cria nova
- Se conversa **já existe**: atualiza `contact_name` e `status` se necessário
- Retorna sempre o `conversation_id`

---

### 2. `POST /messages`

**Descrição:** Registra uma mensagem em uma conversa.

**Request:**
```json
{
  "conversation_id": "uuid-opcional",
  "user_id": "uuid-string",
  "external_contact_id": "5511999887766",
  "direction": "inbound",
  "type": "user",
  "text": "Olá! Como posso te ajudar?",
  "timestamp_ts": 1699999999,
  "metadata": {
    "whatsapp_message_id": "wamid.xxx",
    "phone_number": "5511999887766"
  }
}
```

**Response (201 Created):**
```json
{
  "message_id": "uuid-da-mensagem",
  "conversation_id": "uuid-da-conversa"
}
```

**Lógica:**
- Se `conversation_id` **informado**:
  - Valida se a conversa existe (400 se não existir)
- Se `conversation_id` **não informado**:
  - Busca conversa por `(user_id, external_contact_id)`
  - Se não encontrar, cria nova conversa automaticamente
- Insere a mensagem
- Retorna `message_id` e `conversation_id`

---

## 🗄️ Estrutura de Tabelas Necessárias

### Tabela `conversas`

```sql
CREATE TABLE conversas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  external_contact_id TEXT NOT NULL,
  contact_name TEXT,
  source TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open',
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_id, external_contact_id)
);

CREATE INDEX idx_conversas_user_id ON conversas(user_id);
CREATE INDEX idx_conversas_external_contact ON conversas(external_contact_id);
```

### Tabela `messages`

```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversas(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  external_contact_id TEXT NOT NULL,
  direction TEXT NOT NULL CHECK (direction IN ('inbound', 'outbound')),
  type TEXT NOT NULL,
  text TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
```

---

## 🧪 Como Testar

### 1. Executar o servidor:

```bash
.\.venv\Scripts\activate
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Executar testes:

```bash
python test_conversation_api.py
```

### 3. Testar manualmente (cURL):

**Criar/Atualizar Conversa:**
```bash
curl -X POST http://localhost:8000/conversations/upsert \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "seu-uuid-aqui",
    "external_contact_id": "5511999887766",
    "contact_name": "João Silva",
    "source": "whatsapp",
    "status": "open"
  }'
```

**Criar Mensagem:**
```bash
curl -X POST http://localhost:8000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "seu-uuid-aqui",
    "external_contact_id": "5511999887766",
    "direction": "inbound",
    "type": "user",
    "text": "Olá!"
  }'
```

---

## 🔗 Integração com n8n

### Fluxo Típico:

1. **Webhook n8n** recebe mensagem do WhatsApp
2. **HTTP Request (upsert conversation):**
   ```
   POST http://seu-servidor:8000/conversations/upsert
   Body:
   {
     "user_id": "{{ $json.user_id }}",
     "external_contact_id": "{{ $json.from }}",
     "contact_name": "{{ $json.profile.name }}",
     "source": "whatsapp"
   }
   ```
3. **HTTP Request (create message):**
   ```
   POST http://seu-servidor:8000/messages
   Body:
   {
     "conversation_id": "{{ $json.conversation_id }}",
     "user_id": "{{ $json.user_id }}",
     "external_contact_id": "{{ $json.from }}",
     "direction": "inbound",
     "type": "user",
     "text": "{{ $json.text.body }}",
     "timestamp_ts": "{{ $json.timestamp }}",
     "metadata": {
       "whatsapp_message_id": "{{ $json.id }}"
     }
   }
   ```

---

## ⚠️ Tratamento de Erros

| Status Code | Descrição |
|-------------|-----------|
| **200** | Conversa upserted com sucesso |
| **201** | Mensagem criada com sucesso |
| **400** | Erro de validação (conversation_id inválido) |
| **422** | Erro de validação do Pydantic (campos obrigatórios) |
| **500** | Erro interno do servidor (logs gerados) |

---

## 📊 Logs Gerados

### Conversas:
```
INFO upsert_conversation user_id=xxx contact=5511999887766 source=whatsapp
INFO Updated conversation uuid-xxx with changes: ['contact_name', 'status']
INFO Created new conversation uuid-xxx for user uuid-yyy
```

### Mensagens:
```
INFO create_message user_id=xxx contact=5511999887766 direction=inbound type=user
INFO Created message uuid-aaa for conversation uuid-bbb (direction: inbound, type: user)
INFO No conversation found for user xxx and contact yyy - creating new
```

---

## ✅ Checklist de Implementação

- [x] Models Pydantic com validação
- [x] Services com lógica de negócio isolada
- [x] Rotas REST com documentação automática (FastAPI)
- [x] Tratamento de erros (400, 422, 500)
- [x] Logs estruturados
- [x] Conversão de timestamps Unix → PostgreSQL
- [x] Auto-criação de conversa ao criar mensagem
- [x] Upsert inteligente (cria ou atualiza)
- [x] Metadata JSONB para flexibilidade
- [x] Script de testes

---

## 🚀 Próximos Passos Sugeridos

1. Adicionar RLS (Row Level Security) no Supabase
2. Implementar rate limiting
3. Adicionar autenticação (Bearer token)
4. Criar endpoint `GET /conversations/{id}/messages` para listar mensagens
5. Implementar paginação
6. Adicionar websockets para atualização em tempo real

---

**Implementado por:** GitHub Copilot  
**Data:** 14 de Novembro de 2025

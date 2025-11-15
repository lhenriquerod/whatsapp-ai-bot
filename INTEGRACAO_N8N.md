# 🔧 Guia de Integração N8N - Ajustes Necessários

## 📋 Mudanças Implementadas

Este documento descreve todas as alterações realizadas no microserviço para permitir a integração com n8n e as configurações necessárias.

---

## 1. ⚙️ Configuração de Autenticação Supabase

### ❌ Problema Original
O código estava usando `SUPABASE_ANON_KEY` (chave pública), que é protegida por Row-Level Security (RLS) policies. Isso causava erro:
```
new row violates row-level security policy for table "conversas"
```

### ✅ Solução
Backend services devem usar **Service Role Key** que bypassa RLS.

**Alteração em `.env`:**
```env
# Remova ou comente:
# SUPABASE_ANON_KEY=sua_anon_key

# Adicione:
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Como obter a Service Role Key:**
1. Acesse seu projeto no Supabase Dashboard
2. Settings → API → Project API keys
3. Copie a **service_role** (secret) key
4. Cole no arquivo `.env`

---

## 2. 🔄 Mapeamento de Status

### ❌ Problema Original
A constraint do banco aceita apenas valores em português: `ativa`, `pendente`, `finalizada`, `cancelada`, `arquivada`

### ✅ Solução
O código agora mapeia automaticamente status da API (inglês) para o banco (português).

**Mapeamento implementado:**
```
API (n8n)      →  Banco de Dados
-----------       ---------------
"open"         →  "ativa"
"closed"       →  "finalizada"
"archived"     →  "arquivada"
"pending"      →  "pendente"
"cancelled"    →  "cancelada"
```

**Script SQL executado:**
```sql
-- Arquivo: sql/fix_conversas_status_constraint.sql
ALTER TABLE conversas DROP CONSTRAINT IF EXISTS conversas_status_chk;
ALTER TABLE conversas ALTER COLUMN status SET DEFAULT 'ativa';
ALTER TABLE conversas ADD CONSTRAINT conversas_status_check 
  CHECK (status IN ('ativa', 'pendente', 'finalizada', 'cancelada', 'arquivada'));
```

---

## 3. 🗂️ Mapeamento de Campos

### Campo `source` → `canal`
O campo que armazena a origem da conversa na tabela é `canal`, não `source`.

**Alteração no código:**
```python
# Antes:
"source": request.source

# Depois:
"canal": request.source  # API recebe "source", mas salva em "canal"
```

### Campo `tipo` para mensagens
Mensagens têm mapeamento de tipo:
```
API           →  Banco
-----------      -------
"user"        →  "usuario"
"assistant"   →  "agente"
"system"      →  "agente"
```

---

## 4. 📡 Endpoints para N8N

### POST /conversations/upsert

Garante que existe uma conversa para um contato.

**Request:**
```json
{
  "user_id": "uuid-do-usuario",
  "external_contact_id": "5511999998888",
  "contact_name": "João Silva",
  "source": "whatsapp",
  "status": "open",
  "started_at_ts": 1704067200
}
```

**Response:**
```json
{
  "conversation_id": "uuid-da-conversa",
  "created": true
}
```

**Comportamento:**
- Se conversa **não existe**: cria nova e retorna `created: true`
- Se conversa **já existe**: atualiza `contact_name` e `status`, retorna `created: false`

---

### POST /messages

Registra uma mensagem em uma conversa.

**Request:**
```json
{
  "user_id": "uuid-do-usuario",
  "external_contact_id": "5511999998888",
  "contact_name": "João Silva",
  "source": "whatsapp",
  "direction": "inbound",
  "type": "user",
  "text": "Olá, preciso de ajuda!",
  "metadata": {
    "message_id": "wamid.123456",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

**Response:**
```json
{
  "message_id": "uuid-da-mensagem",
  "conversation_id": "uuid-da-conversa"
}
```

**Comportamento:**
- Se `conversation_id` não informado: busca/cria conversa automaticamente
- Insere mensagem na tabela `mensagens`
- Retorna IDs da mensagem e conversa

---

## 5. 🎯 Configuração no N8N

### Fluxo Recomendado

```
┌─────────────────┐
│ Webhook WhatsApp│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│ HTTP Request                    │
│ POST /conversations/upsert      │
│ Body:                           │
│   user_id: {{ $json.user_id }}  │
│   external_contact_id: {{ ...}} │
│   contact_name: {{ ... }}       │
│   source: "whatsapp"            │
│   status: "open"                │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ HTTP Request                    │
│ POST /messages                  │
│ Body:                           │
│   user_id: {{ $json.user_id }}  │
│   external_contact_id: {{ ...}} │
│   direction: "inbound"          │
│   type: "user"                  │
│   text: {{ $json.message }}     │
│   metadata: {{ ... }}           │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Processar com IA / Lógica       │
└─────────────────────────────────┘
```

### Exemplo de HTTP Request Node (N8N)

**Node 1: Upsert Conversation**
```
Method: POST
URL: http://seu-servidor:8000/conversations/upsert
Headers:
  Content-Type: application/json
Body (JSON):
{
  "user_id": "{{ $json.user_id }}",
  "external_contact_id": "{{ $json.from }}",
  "contact_name": "{{ $json.contact_name }}",
  "source": "whatsapp",
  "status": "open"
}
```

**Node 2: Create Message**
```
Method: POST
URL: http://seu-servidor:8000/messages
Headers:
  Content-Type: application/json
Body (JSON):
{
  "user_id": "{{ $json.user_id }}",
  "external_contact_id": "{{ $json.from }}",
  "direction": "inbound",
  "type": "user",
  "text": "{{ $json.message }}",
  "metadata": {
    "whatsapp_message_id": "{{ $json.id }}",
    "timestamp": "{{ $json.timestamp }}"
  }
}
```

---

## 6. 🔑 Valores Importantes

### Status (use em inglês na API)
- `"open"` - Conversa ativa
- `"closed"` - Conversa finalizada
- `"archived"` - Conversa arquivada
- `"pending"` - Aguardando resposta
- `"cancelled"` - Conversa cancelada

### Direction (mensagens)
- `"inbound"` - Mensagem recebida (do contato)
- `"outbound"` - Mensagem enviada (para o contato)

### Type (mensagens)
- `"user"` - Mensagem do usuário/contato
- `"assistant"` - Mensagem do assistente/bot
- `"system"` - Mensagem do sistema

### Source
- `"whatsapp"` - Origem WhatsApp
- `"simulacao"` - Teste/simulação
- Outros valores personalizados conforme necessário

---

## 7. ✅ Checklist de Configuração

Antes de integrar com n8n, verifique:

- [ ] Variável `SUPABASE_SERVICE_ROLE_KEY` configurada no `.env`
- [ ] Servidor rodando: `uvicorn app:app --host 0.0.0.0 --port 8000`
- [ ] Constraint de status corrigida (executar `sql/fix_conversas_status_constraint.sql`)
- [ ] Pelo menos 1 usuário cadastrado na tabela `usuarios`
- [ ] Endpoints testados com `test_n8n_payload.py`

---

## 8. 🧪 Testando Localmente

Execute o script de teste:
```bash
python test_n8n_payload.py
```

**Resultado esperado:**
```
✅ SUCCESS!
Conversation ID: db46338c-0396-4d90-b941-9df099daf2d3
Created: True

✅ SUCCESS!
Message ID: 53252987-6242-4baf-a8dd-75f7335e3a99
Conversation ID: db46338c-0396-4d90-b941-9df099daf2d3
```

---

## 9. ⚠️ Troubleshooting

### Erro: "violates row-level security policy"
**Causa:** Usando `SUPABASE_ANON_KEY` em vez de `SUPABASE_SERVICE_ROLE_KEY`  
**Solução:** Atualizar `.env` com a service role key

### Erro: "violates check constraint conversas_status_check"
**Causa:** Constraint não aceita o valor de status enviado  
**Solução:** Executar `sql/fix_conversas_status_constraint.sql` no Supabase

### Erro: "violates foreign key constraint conversas_user_id_fkey"
**Causa:** `user_id` não existe na tabela `usuarios`  
**Solução:** Criar usuário ou usar UUID de usuário existente

### Erro: "column conversas.source does not exist"
**Causa:** Campo correto é `canal`, não `source`  
**Solução:** Código já corrigido, garantir versão atualizada

---

## 10. 📝 Resumo das Alterações de Código

### Arquivos modificados:
- `src/utils/config.py` - Mudou `SUPABASE_ANON_KEY` para `SUPABASE_SERVICE_ROLE_KEY`
- `src/services/supabase_service.py` - Atualizado para usar nova key
- `src/services/conversation_service.py` - Mapeamento status e campo `canal`
- `src/services/message_service.py` - Mapeamento tipo de mensagem
- `README.md` - Atualizada documentação das variáveis de ambiente

### Arquivos criados:
- `sql/fix_conversas_status_constraint.sql` - Script para corrigir constraint
- `test_n8n_payload.py` - Script de teste dos endpoints
- `list_users.py` - Script para listar usuários
- `INTEGRACAO_N8N.md` - Este documento

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do servidor: terminal onde `uvicorn` está rodando
2. Execute `python list_users.py` para ver usuários disponíveis
3. Execute `python test_n8n_payload.py` para validar endpoints
4. Verifique se a constraint foi corrigida no Supabase SQL Editor

---

**Última atualização:** 14 de Novembro de 2025

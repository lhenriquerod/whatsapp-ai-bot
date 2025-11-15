# Problema: Quebras de Linha não Aparecem no WhatsApp

## 🔍 Diagnóstico Completo

### ✅ Backend FastAPI
**Status:** ✅ FUNCIONANDO CORRETAMENTE

**Teste realizado:**
```bash
python test_quebras_linha.py
```

**Resultado:**
- API retorna **17 quebras de linha** (`\n`)
- Resposta bem formatada
- Instruções de formatação OK

**Resposta da API (raw):**
```python
'Atualmente, temos o *Plano Essencial* disponível.\n\n*Plano Essencial*\n💰 R$ 260/mês...'
```

### ❌ WhatsApp/n8n
**Status:** ❌ REMOVENDO QUEBRAS DE LINHA

O n8n ou WhatsApp está convertendo `\n` em espaços.

## 🎯 Localização do Problema

**✅ NÃO é aqui (tudo OK):**
- `personality_service.py` - Instruções de formatação
- `ai_service.py` - OpenAI retornando corretamente
- `app.py` - FastAPI retornando com `\n`

**❌ É aqui (precisa ajustar):**
- Fluxo n8n que envia para WhatsApp
- Configuração da API do WhatsApp
- Encoding/escaping da mensagem

## 🔧 Soluções por Plataforma

### 1️⃣ n8n - HTTP Request Node

**Verifique o nó que chama a API do WhatsApp:**

#### ❌ ERRADO - Processando como HTML/String
```javascript
// Se tiver algo assim no n8n:
{{ $json.reply.replace('\n', ' ') }}  // Remove quebras
{{ $json.reply.trim() }}              // Remove formatação
```

#### ✅ CORRETO - Passar direto
```javascript
// Simplesmente use:
{{ $json.reply }}

// Ou garanta que está preservando:
{{ $json.reply.replace(/\\n/g, '\n') }}
```

### 2️⃣ WhatsApp Business API (Meta)

**Endpoint:** `https://graph.facebook.com/v18.0/{phone-id}/messages`

**Body correto:**
```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "5511999999999",
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "{{ $json.reply }}"
  }
}
```

**⚠️ Importante:**
- Use `\n` para quebras de linha
- **NÃO** use `<br>` ou `\r\n`
- **NÃO** faça URL encoding do body

### 3️⃣ Evolution API

**Endpoint:** `http://seu-servidor/message/sendText/{instance}`

**Body correto:**
```json
{
  "number": "5511999999999",
  "text": "{{ $json.reply }}"
}
```

**ou:**

```json
{
  "number": "5511999999999",
  "textMessage": {
    "text": "{{ $json.reply }}"
  }
}
```

### 4️⃣ Twilio API

**Endpoint:** `https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json`

**Body (x-www-form-urlencoded):**
```
To=whatsapp:+5511999999999
From=whatsapp:+14155238886
Body={{ $json.reply }}
```

**⚠️ Importante:**
- Twilio preserva `\n` automaticamente
- Use Content-Type: `application/x-www-form-urlencoded`

## 🧪 Como Testar

### Teste 1: Verificar o que o n8n está enviando

No n8n, adicione um nó "Edit Fields" ou "Set" ANTES de enviar para o WhatsApp:

```javascript
// Ver o que está sendo enviado
console.log('Reply:', JSON.stringify($json.reply));
console.log('Quebras:', ($json.reply.match(/\n/g) || []).length);
```

### Teste 2: Enviar manualmente via Postman

```bash
# Pegue a resposta da API
curl http://localhost:8000/simulation/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "seu-id", "message": "Quais planos?"}'

# Copie a resposta e envie direto para WhatsApp
# Se funcionar no Postman mas não no n8n, o problema é no n8n
```

### Teste 3: Log do n8n

Ative o debug no n8n e veja o payload exato sendo enviado:

```json
{
  "text": "Plano Essencial: R$ 260/mês..." // ❌ Sem \n = problema
  "text": "Plano Essencial:\nR$ 260/mês..." // ✅ Com \n = OK
}
```

## 📋 Checklist de Verificação

### No n8n:
- [ ] O campo `reply` está sendo usado diretamente (sem `.trim()`, `.replace()`, etc)?
- [ ] O Content-Type está correto (`application/json`)?
- [ ] Não há encoding extra (URL encoding, base64, etc)?
- [ ] O nó HTTP Request está em modo `JSON` (não Form ou Raw)?

### Na API do WhatsApp:
- [ ] O campo `body` ou `text` recebe o conteúdo com `\n`?
- [ ] Não há processamento de HTML ou Markdown?
- [ ] A API suporta `\n` (algumas versões antigas não suportam)?

### No Backend (já verificado ✅):
- [x] FastAPI retorna com `\n`
- [x] Instruções de formatação adicionadas
- [x] OpenAI gerando quebras de linha

## 🎯 Solução Rápida

Se nada funcionar, tente estas alternativas:

### Alternativa 1: Forçar quebra dupla
```javascript
// No n8n, antes de enviar:
{{ $json.reply.replace(/\n/g, '\n\n') }}
```

### Alternativa 2: Usar caractere visível como separador
```javascript
// Adicionar linha tracejada entre seções
{{ $json.reply.replace(/\n\n/g, '\n━━━━━━━\n') }}
```

### Alternativa 3: Enviar múltiplas mensagens
```javascript
// Dividir em mensagens separadas
const parts = $json.reply.split('\n\n');
// Enviar cada parte como uma mensagem
```

## 📞 Exemplo Completo n8n

```
[Webhook] → [HTTP Request: FastAPI] → [Edit Fields] → [HTTP Request: WhatsApp]
                                           ↓
                                   Verificar reply
                                   preserva \n
```

**Configuração do "Edit Fields":**
```json
{
  "whatsapp_message": {
    "to": "{{ $('Webhook').item.json.from }}",
    "text": "{{ $('HTTP Request').item.json.reply }}"
  }
}
```

**Configuração do "HTTP Request: WhatsApp":**
- Method: POST
- URL: `https://api.whatsapp.com/...`
- Body: `{{ $json.whatsapp_message }}`
- Content-Type: `application/json`

## 🆘 Se nada funcionar

**Última opção - Modificar o backend para HTML:**

```python
# app.py - adicionar conversão
reply = reply.replace('\n', '<br>')  # Para web
# ou
reply = reply.replace('\n', '\n\n')  # Forçar duplo
```

Mas isso **NÃO deveria ser necessário**. O problema está no n8n/WhatsApp.

## 📚 Referências

- [WhatsApp Business API - Text Messages](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages)
- [Evolution API - Send Text](https://doc.evolution-api.com/v2/pt/send-messages/text)
- [n8n - HTTP Request Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)

## ✅ Conclusão

**O backend está perfeito.** O problema está em como o n8n ou WhatsApp API está processando a mensagem.

**Próximos passos:**
1. Verificar o fluxo n8n
2. Ver o payload enviado para WhatsApp
3. Testar manualmente via Postman
4. Ajustar o nó HTTP Request do n8n

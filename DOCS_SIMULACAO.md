# 🧪 Modo Simulação - Documentação

## Visão Geral

A rota `POST /simulation/chat` foi criada especificamente para o **modo simulação do painel web**, permitindo que usuários testem seus agentes conversacionais sem necessidade de integração com WhatsApp ou registro de conversas.

---

## 🎯 Objetivo

Permitir que usuários testem:
- Respostas do agente baseadas na base de conhecimento
- Personalidade configurada (tom de voz, prompt personalizado)
- Contexto e comportamento do agente em tempo real
- Ajustes de configuração antes de colocar em produção

---

## 🔄 Diferenças entre `/chat` e `/simulation/chat`

| Aspecto | `/chat` | `/simulation/chat` |
|---------|---------|-------------------|
| **Propósito** | Produção (integração n8n/WhatsApp) | Testes no painel web |
| **Registra conversas** | Não (gerenciado pelo n8n) | ❌ Não registra nada |
| **Registra mensagens** | Não (gerenciado pelo n8n) | ❌ Não registra nada |
| **Usa base de conhecimento** | ✅ Sim | ✅ Sim |
| **Usa configuração do usuário** | ✅ Sim | ✅ Sim |
| **Personalidade/Tom de voz** | ✅ Sim | ✅ Sim |
| **Headers suportados** | `X-Request-Id` | `X-Request-Id` |

---

## 📝 Estrutura de Dados

### Request
```typescript
{
  user_id: string;    // UUID do usuário (obrigatório)
  message: string;    // Mensagem para testar (obrigatório)
}
```

### Response
```typescript
{
  reply: string;           // Resposta gerada pela IA
  source: string;          // Sempre "supabase"
  request_id?: string;     // ID de rastreamento (se enviado no header)
}
```

---

## 🔧 Implementação Técnica

### Lógica Compartilhada

Ambas as rotas (`/chat` e `/simulation/chat`) utilizam a mesma função interna:

```python
def generate_agent_reply(user_id: str, message: str, x_request_id: Optional[str]) -> ChatOut:
    """
    Gera resposta do agente usando:
    1. Contexto da base de conhecimento (get_context)
    2. Configurações do usuário (get_user_config)
    3. System prompt personalizado (build_system_prompt)
    4. IA (AIService.generate_response)
    """
```

### Fluxo de Execução

```
┌─────────────────────────┐
│ POST /simulation/chat   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ generate_agent_reply()              │
├─────────────────────────────────────┤
│ 1. get_context(user_id)            │
│    → Busca base_conhecimento        │
│                                     │
│ 2. get_user_config(user_id)        │
│    → Busca configuracao_empresa     │
│    → Obtém tom_voz, personalidade   │
│                                     │
│ 3. build_system_prompt()           │
│    → Monta prompt com config        │
│                                     │
│ 4. ai.generate_response()          │
│    → OpenAI GPT-4o-mini            │
└───────────┬─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│ SimulationChatOut       │
│ {                       │
│   reply: "...",         │
│   source: "supabase",   │
│   request_id: "..."     │
│ }                       │
└─────────────────────────┘
```

---

## 🎨 Personalização

A rota respeita as configurações do usuário armazenadas em `configuracao_empresa`:

### Tom de Voz
```python
tom_voz_options = {
    "formal": "Mantenha um tom formal e profissional.",
    "amigavel": "Mantenha um tom amigável e acolhedor.",
    "objetivo": "Seja direto e objetivo nas respostas.",
    "descontraido": "Use um tom descontraído e informal."
}
```

### Personalidade Customizada
Se o usuário configurou `prompt_base_persona`, este será usado **em vez** do prompt padrão.

Exemplo:
```sql
UPDATE configuracao_empresa 
SET prompt_base_persona = 'Você é a Clara, assistente virtual da Loja XYZ. 
Seja simpática, use emojis e trate todos por "você".'
WHERE user_id = 'uuid-do-usuario';
```

---

## 🧪 Testes

### Teste Simples
```bash
curl -X POST http://localhost:8000/simulation/chat \
  -H "Content-Type: application/json" \
  -H "X-Request-Id: test-sim-001" \
  -d '{
    "user_id": "6bf0dab0-e895-4730-b5fa-cd8acff6de0c",
    "message": "Olá! Quais produtos vocês vendem?"
  }'
```

### Teste com Script Python
```bash
python test_simulation_endpoint.py
```

O script `test_simulation_endpoint.py` executa:
1. Teste de mensagem única
2. Sequência de múltiplas mensagens (simulando conversa)

---

## 📊 Logs

A rota gera logs estruturados seguindo o padrão da aplicação:

**Início da requisição:**
```
chat_simulation_start user=***de0c request_id=test-123
```

**Sucesso:**
```
chat_simulation_success user=***de0c request_id=test-123 elapsed_ms=1245
```

**Erro:**
```
chat_simulation_error request_id=test-123 elapsed_ms=892 error=...
```

---

## ⚠️ Importante

### O que NÃO faz:
- ❌ Não cria registros em `conversas`
- ❌ Não cria registros em `mensagens`
- ❌ Não integra com WhatsApp
- ❌ Não chama webhooks do n8n
- ❌ Não persiste histórico de conversa

### O que FAZ:
- ✅ Busca contexto da base de conhecimento
- ✅ Usa configurações personalizadas do usuário
- ✅ Gera respostas via OpenAI
- ✅ Retorna resposta imediata
- ✅ Registra logs para debugging

---

## 🔐 Segurança

- User ID é mascarado nos logs (`***de0c`)
- Usa mesmas credenciais OpenAI do `/chat`
- Validação Pydantic nos inputs
- Error handling com HTTPException
- CORS configurado (ajustar origins para produção)

---

## 📚 Arquivos Relacionados

- `app.py` - Rota `/simulation/chat` (linha ~158)
- `src/services/user_config_service.py` - Busca configurações
- `src/services/supabase_service.py` - Busca contexto
- `src/services/ai_service.py` - Geração de resposta
- `test_simulation_endpoint.py` - Script de testes

---

## 🚀 Próximos Passos

Para usar no painel web:

1. **Frontend:** Criar interface de chat para modo simulação
2. **State Management:** Manter histórico local (apenas no frontend)
3. **UX:** Indicar claramente que é modo teste
4. **Botão "Testar Agente":** Abrir modal/sidebar com chat simulado
5. **Salvar configurações:** Permitir ajustar tom_voz e testar em tempo real

---

**Última atualização:** 15 de Novembro de 2025

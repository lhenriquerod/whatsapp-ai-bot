# Migração Backend: Português → Inglês

## 📋 STATUS DA MIGRAÇÃO

✅ **Backend FastAPI**: Migração completa  
⚠️ **Database Supabase**: Assumido como já migrado (script 008_rename_to_english.sql)

---

## 🎯 ALTERAÇÕES REALIZADAS NO BACKEND

### 1. **src/utils/config.py**
```python
# ANTES
KB_TABLE = "base_conhecimento"
KB_FIELDS = "categoria,dados"

# DEPOIS
KB_TABLE = "knowledge_base"
KB_FIELDS = "category,data"
```

### 2. **src/services/message_service.py**
- `conversas` → `conversations`
- `mensagens` → `messages`
- `conversa_id` → `conversation_id`
- `tipo` → `type`
- `mensagem` → `message`
- Removido mapeamento de valores: `usuario/agente` → `user/agent` (banco já está em inglês)

### 3. **src/services/conversation_service.py**
- `conversas` → `conversations`
- `titulo` → `title`
- `canal` → `channel`
- `iniciada_em` → `started_at`
- Removido mapeamento de status: `ativa/finalizada/arquivada` → `open/closed/archived`

### 4. **src/services/personality_service.py**
- `personalidade_agente` → `agent_personality`
- `nome` → `name`
- `nivel_personalidade` → `personality_level`
- `tom_voz` → `voice_tone`
- `forma_tratamento` → `address_form`
- `apresentacao_inicial` → `initial_message`
- Constantes renomeadas: `NIVEIS_PERSONALIDADE` → `PERSONALITY_LEVELS`
- Constantes renomeadas: `TOM_VOZ_INSTRUCOES` → `VOICE_TONE_INSTRUCTIONS`

### 5. **src/services/supabase_service.py**
- `base_conhecimento` → `knowledge_base`
- `categoria` → `category`
- `dados` → `data`
- Categorias: `produto/servico/empresa/personalizado` → `product/service/company/custom`

### 6. **src/services/user_config_service.py**
- `configuracao_empresa` → `company_settings`

### 7. **app.py**
- Campo `mensagem` → `message` no histórico de mensagens

### 8. **Arquivos de teste (16 arquivos)**
✅ Migrados automaticamente via script `migrate_test_files.py`
- Total de substituições: 141 mudanças

---

## 📊 MAPEAMENTO COMPLETO

### **Tabelas**
| Português (ANTIGO) | Inglês (NOVO) |
|-------------------|---------------|
| conversas | conversations |
| mensagens | messages |
| base_conhecimento | knowledge_base |
| personalidade_agente | agent_personality |
| configuracao_empresa | company_settings |

### **Campos - conversations**
| Português | Inglês |
|-----------|--------|
| titulo | title |
| canal | channel |
| iniciada_em | started_at |
| finalizada_em | ended_at |
| total_mensagens | total_messages |

### **Campos - messages**
| Português | Inglês |
|-----------|--------|
| conversa_id | conversation_id |
| tipo | type |
| mensagem | message |

### **Campos - knowledge_base**
| Português | Inglês |
|-----------|--------|
| categoria | category |
| dados | data |

### **Campos - agent_personality**
| Português | Inglês |
|-----------|--------|
| nome | name |
| nivel_personalidade | personality_level |
| tom_voz | voice_tone |
| forma_tratamento | address_form |
| apresentacao_inicial | initial_message |

### **Valores ENUM - category**
| Português | Inglês |
|-----------|--------|
| produto | product |
| servico | service |
| empresa | company |
| faq | faq *(sem mudança)* |
| personalizado | custom |

### **Valores ENUM - type**
| Português | Inglês |
|-----------|--------|
| usuario | user |
| agente | agent |
| sistema | system |

### **Valores ENUM - status**
| Português | Inglês |
|-----------|--------|
| ativa | open |
| finalizada | closed |
| arquivada | archived |

### **Valores ENUM - voice_tone**
| Português | Inglês |
|-----------|--------|
| formal | formal *(sem mudança)* |
| amigavel | friendly |
| objetivo | objective |
| descontraido | casual |

### **Valores ENUM - address_form**
| Português | Inglês |
|-----------|--------|
| voce | you_informal |
| senhor | you_formal |
| informal | sir_madam |

---

## 🚀 ARQUIVOS MODIFICADOS

### **Código Principal**
1. ✅ `src/utils/config.py`
2. ✅ `src/services/message_service.py`
3. ✅ `src/services/conversation_service.py`
4. ✅ `src/services/personality_service.py`
5. ✅ `src/services/supabase_service.py`
6. ✅ `src/services/user_config_service.py`
7. ✅ `app.py`

### **Arquivos de Teste** (16 arquivos)
1. ✅ test_all_status_values.py (6 substituições)
2. ✅ test_chat_with_history.py (2 substituições)
3. ✅ test_contact_name.py (2 substituições)
4. ✅ test_conversation_history.py (28 substituições)
5. ✅ test_empresa_format.py (7 substituições)
6. ✅ test_knowledge_base.py (30 substituições)
7. ✅ test_personality_integration.py (32 substituições)
8. ✅ test_produto_com_planos.py (25 substituições)
9. ✅ test_status_default.py (9 substituições)
10. ⏭️ test_formatacao_resposta.py (sem mudanças)
11. ⏭️ test_get_context.py (sem mudanças)
12. ⏭️ test_get_history_function.py (sem mudanças)
13. ⏭️ test_n8n_payload.py (sem mudanças)
14. ⏭️ test_quebras_linha.py (sem mudanças)
15. ⏭️ test_simple_chat.py (sem mudanças)
16. ⏭️ test_simulation_endpoint.py (sem mudanças)

### **Scripts Utilitários**
- ✅ `migrate_test_files.py` (criado para automação)

---

## ⚠️ PONTOS DE ATENÇÃO

### 1. **Remoção de Mapeamentos**
Anteriormente, o código fazia mapeamento de valores:
- `user/assistant` → `usuario/agente` ✅ REMOVIDO
- `open/closed` → `ativa/finalizada` ✅ REMOVIDO

**Motivo**: O banco agora usa inglês nativamente.

### 2. **Normalização de Valores**
- `assistant` → `agent` (normalização mantida no código)
- Todos os outros valores já correspondem aos do banco

### 3. **Retro Compatibilidade**
❌ **Não há compatibilidade** com dados antigos em português.  
Se houver dados legados, execute a migração SQL primeiro.

---

## 🧪 TESTES PENDENTES

### **Executar após migração**
```bash
# 1. Teste de criação de mensagem
python test_conversation_history.py

# 2. Teste de personalidade
python test_personality_integration.py

# 3. Teste de base de conhecimento
python test_knowledge_base.py

# 4. Teste de status
python test_all_status_values.py

# 5. Teste do endpoint /chat
python test_simple_chat.py
```

### **Verificar funcionalidades**
- [ ] Criação de conversas (status em inglês)
- [ ] Criação de mensagens (type em inglês)
- [ ] Histórico de conversação (conversation_id, message)
- [ ] Busca de personalidade (agent_personality)
- [ ] Busca de base de conhecimento (knowledge_base, category, data)
- [ ] Endpoint `/chat` com external_contact_id
- [ ] Endpoint `/simulation/chat`

---

## 📝 EXEMPLO DE USO

### **Antes (Português)**
```python
# Criar mensagem
result = _client.table("mensagens").insert({
    "conversa_id": "uuid",
    "tipo": "usuario",
    "mensagem": "Olá"
}).execute()

# Buscar base de conhecimento
kb = _client.table("base_conhecimento").select("categoria, dados").execute()
```

### **Depois (Inglês)**
```python
# Criar mensagem
result = _client.table("messages").insert({
    "conversation_id": "uuid",
    "type": "user",
    "message": "Olá"
}).execute()

# Buscar base de conhecimento
kb = _client.table("knowledge_base").select("category, data").execute()
```

---

## ✅ CHECKLIST FINAL

### **Backend**
- [x] config.py atualizado (KB_TABLE, KB_FIELDS)
- [x] message_service.py migrado
- [x] conversation_service.py migrado
- [x] personality_service.py migrado
- [x] supabase_service.py migrado
- [x] user_config_service.py migrado
- [x] app.py atualizado
- [x] Testes automatizados migrados (16 arquivos)
- [x] Sem erros de compilação

### **Database**
- [ ] Script SQL 008_rename_to_english.sql executado no Supabase
- [ ] Dados migrados (TRUNCATE executado conforme documentação)

### **Validação**
- [ ] Executar todos os testes
- [ ] Testar `/chat` endpoint
- [ ] Testar `/simulation/chat` endpoint
- [ ] Verificar logs para erros
- [ ] Testar integração n8n

---

## 🆘 TROUBLESHOOTING

### **Erro: Table 'conversas' does not exist**
✅ **Solução**: Execute o script SQL de migração no Supabase primeiro

### **Erro: Column 'categoria' does not exist**
✅ **Solução**: Verifique se o script SQL renomeou todos os campos

### **Erro: Type 'usuario' is not assignable**
✅ **Solução**: O código já não usa valores em português, verifique se há código legado

### **Dados não aparecem**
✅ **Solução**: Popule novamente a base com dados de teste usando os scripts test_*.py

---

**Data**: 2025-11-17  
**Autor**: GitHub Copilot  
**Revisão**: Backend Migration v1.0

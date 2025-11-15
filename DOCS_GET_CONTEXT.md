# 📚 Implementação get_context() - Documentação

## ✅ Implementação Completa

A função `get_context()` foi implementada para buscar dados reais do Supabase na tabela `base_conhecimento`.

---

## 🔧 Como Funciona

### Estrutura da Tabela `base_conhecimento`

```sql
CREATE TABLE base_conhecimento (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    categoria VARCHAR(50) NOT NULL,  -- 'produto', 'servico', 'empresa', 'faq', 'personalizado'
    dados JSONB NOT NULL,             -- Estrutura flexível por categoria
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Categorias Suportadas

| Categoria | Campos JSONB | Exemplo |
|-----------|--------------|---------|
| **produto** | nome, descricao, preco, caracteristicas | Notebook Dell i7 |
| **servico** | nome, descricao, duracao, preco | Consultoria TI |
| **empresa** | topico, conteudo | Horário de funcionamento |
| **faq** | pergunta, resposta | Qual prazo de entrega? |
| **personalizado** | campos flexíveis | Política de troca |

---

## 📝 Função get_context()

### Assinatura
```python
def get_context(owner_id: str) -> str
```

### Comportamento

1. **Busca registros** na tabela `base_conhecimento` onde `user_id = owner_id`
2. **Formata cada registro** de acordo com sua categoria
3. **Retorna string formatada** com todos os itens, ou mensagem padrão se vazio

### Formato de Saída

```
Base de conhecimento:

- Produto: Notebook Dell Inspiron 15 | Descrição: ... | Preço: R$ 3.499,00 | Características: 16GB RAM, SSD 512GB
- Serviço: Consultoria em TI | Descrição: ... | Duração: 10-40 horas | Preço: R$ 200/hora
- Tópico: Horário de Funcionamento | Conteúdo: Segunda a sexta, 9h às 18h
- Pergunta: Qual o prazo de entrega? | Resposta: 3 dias úteis para capital, 7 para interior
```

### Caso Sem Dados

Se não houver registros:
```
Nenhuma base de conhecimento cadastrada para este usuário.
```

---

## 🔄 Integração com Rotas

### Rota `/chat`
```python
@app.post("/chat")
def chat(payload: ChatIn):
    # ...
    result = generate_agent_reply(
        user_id=payload.user_id,
        message=payload.message
    )
    return result
```

### Rota `/simulation/chat`
```python
@app.post("/simulation/chat")
def simulation_chat(payload: SimulationChatIn):
    # ...
    result = generate_agent_reply(
        user_id=payload.user_id,
        message=payload.message
    )
    return result
```

### Função Compartilhada `generate_agent_reply()`
```python
def generate_agent_reply(user_id: str, message: str) -> ChatOut:
    # 1. Buscar contexto do Supabase
    context = get_context(owner_id=user_id)
    
    # 2. Buscar configuração do usuário
    user_config = get_user_config(user_id)
    
    # 3. Montar system prompt personalizado
    system_prompt = build_system_prompt(context, user_config)
    
    # 4. Montar user prompt com contexto
    user_prompt = f"Contexto:\n{context}\n\nPergunta:\n{message}"
    
    # 5. Gerar resposta da IA
    reply = ai.generate_response(system_prompt, user_prompt)
    
    return ChatOut(reply=reply, source="supabase")
```

---

## 🧪 Como Testar

### 1. Verificar contexto atual
```bash
python test_get_context.py
```

### 2. Inserir dados de exemplo
```bash
python test_knowledge_base.py
```

Este script:
- ✅ Remove dados antigos do usuário
- ✅ Insere 8 exemplos (produtos, serviços, FAQs, etc.)
- ✅ Testa `get_context()` e exibe resultado

### 3. Testar via API

**Teste /chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "6bf0dab0-e895-4730-b5fa-cd8acff6de0c",
    "message": "Quais produtos vocês vendem?"
  }'
```

**Teste /simulation/chat:**
```bash
curl -X POST http://localhost:8000/simulation/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "6bf0dab0-e895-4730-b5fa-cd8acff6de0c",
    "message": "Qual o horário de funcionamento?"
  }'
```

---

## 📊 Logs

A função gera logs estruturados:

**Sucesso:**
```
INFO - Retrieved 8 KB entries for owner=***de0c
```

**Vazio:**
```
INFO - No knowledge base entries found for owner=***de0c
```

**Erro:**
```
ERROR - Failed to fetch context from Supabase for owner=***de0c: [erro]
```

---

## ⚙️ Configuração

As configurações estão em `src/utils/config.py`:

```python
KB_TABLE = "base_conhecimento"      # Nome da tabela
KB_OWNER_COL = "user_id"            # Coluna de filtro
KB_FIELDS = "categoria,dados"       # Campos a buscar
KB_LIMIT = 10                       # Limite de registros
```

---

## 🚀 Próximos Passos (Futuro)

### Campo `ativo` (Opcional)
Se adicionar um campo `ativo` na tabela:

```sql
ALTER TABLE base_conhecimento ADD COLUMN ativo BOOLEAN DEFAULT TRUE;
```

A função já está preparada para filtrar apenas registros ativos (comentário no código).

### Embeddings e Busca Semântica
Atualmente: concatenação simples de textos  
Futuro: usar embeddings + similarity search para RAG avançado

### Cache
Implementar cache Redis para reduzir chamadas ao Supabase em produção.

---

## 📁 Arquivos Relacionados

- `src/services/supabase_service.py` - Implementação de `get_context()`
- `src/services/user_config_service.py` - Busca configuração do usuário
- `app.py` - Rotas `/chat` e `/simulation/chat`
- `test_knowledge_base.py` - Script para inserir dados de exemplo
- `test_get_context.py` - Script para testar apenas a consulta

---

## ✅ Checklist de Implementação

- [x] Função `get_context()` implementada
- [x] Suporte a 5 categorias (produto, servico, empresa, faq, personalizado)
- [x] Formatação por categoria com campos específicos
- [x] Logs estruturados com mascaramento de user_id
- [x] Tratamento de erro com fallback
- [x] Integração com `/chat` e `/simulation/chat`
- [x] Scripts de teste criados
- [x] Documentação completa

---

**Data:** 15 de Novembro de 2025  
**Status:** ✅ Implementado e funcionando

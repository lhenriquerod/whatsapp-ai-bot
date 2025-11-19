# 🚀 Quick Start - RAG com Embeddings Vetoriais

## Passo 1: Executar Migrations no Supabase

### 1.1 Corrigir Foreign Keys (CRÍTICO - Execute primeiro!)

**Arquivo:** `sql/030_fix_conversations_fk_to_users.sql`

1. Acesse seu projeto no Supabase
2. Vá em **SQL Editor** → **New Query**
3. Cole o conteúdo do arquivo `sql/030_fix_conversations_fk_to_users.sql`
4. Execute (Run)

**O que faz:**
- Remove constraint antiga que referencia `usuarios` (não existe mais)
- Cria nova constraint apontando para `users`
- Permite inserir dados em `conversations` e `messages`

### 1.2 Criar Função de Busca Vetorial

**Arquivo:** `sql/029_create_match_knowledge_chunks_function.sql`

1. No mesmo SQL Editor do Supabase
2. Nova Query
3. Cole o conteúdo do arquivo `sql/029_create_match_knowledge_chunks_function.sql`
4. Execute (Run)

**O que faz:**
- Cria função `match_knowledge_chunks()` para busca semântica
- Usa pgvector para calcular similaridade de cosseno
- Retorna TOP-K chunks mais relevantes

---

## Passo 2: Processar Base de Conhecimento

### 2.1 Certifique-se que o servidor está rodando

```powershell
# Terminal 1 (uvicorn)
uvicorn app:app --reload
```

Deve aparecer:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2.2 Processar chunks

**Opção A: Via curl (PowerShell)**

```powershell
$USER_ID = "e35af3a4-a7e6-422f-a483-bbcfc9d7c24f"
curl.exe -X POST "http://localhost:8000/knowledge/process-chunks/$USER_ID"
```

**Opção B: Via Python test script**

```powershell
# Terminal 2 (PowerShell separado)
.\.venv\Scripts\python.exe test_rag_e2e.py
```

**Resultado esperado:**
```json
{
  "message": "Chunks processados e embeddings gerados com sucesso",
  "knowledge_entries": 5,
  "chunks_created": 23,
  "processing_time_ms": 1847
}
```

**Verifique no Supabase:**
- Tabela `knowledge_chunks` deve ter registros
- Cada registro tem campo `embedding` (vector 1536 dims)

---

## Passo 3: Testar Chat com Busca Semântica

### 3.1 Teste via curl

```powershell
curl.exe -X POST http://localhost:8000/simulation/chat `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":\"e35af3a4-a7e6-422f-a483-bbcfc9d7c24f\",\"message\":\"O RAG-E tem período de teste grátis?\"}'
```

### 3.2 Teste via script Python

```powershell
.\.venv\Scripts\python.exe test_rag_e2e.py
```

### 3.3 O que observar nos logs (terminal uvicorn)

**✅ Sucesso - Vector Search Funcionando:**
```
INFO: Using vector search results
INFO: Found 5 similar chunks (threshold: 0.7)
INFO: Built context with 5 chunks (823 chars)
```

**⚠️ Fallback - Usando busca antiga:**
```
INFO: Vector search empty, falling back to original get_context()
```

Motivos para fallback:
- Tabela `knowledge_chunks` vazia → rode `process-chunks` primeiro
- Nenhum chunk com similaridade >= 0.7 → pergunta muito diferente da base
- Função `match_knowledge_chunks()` não existe → execute migration 029

---

## Passo 4: Comparar Resultados

### Antes (busca textual):
```
Query: "Tem desconto?"
→ Retorna TODA a base de conhecimento
→ LLM precisa filtrar manualmente
→ Contexto pode ter 5000+ caracteres
```

### Agora (busca semântica):
```
Query: "Tem desconto?"
→ Busca embeddings similares
→ Retorna apenas 5 chunks mais relevantes
→ Contexto otimizado (~800 caracteres)
→ Resposta mais precisa e rápida
```

---

## Troubleshooting

### ❌ Erro: "relation usuarios does not exist"

**Causa:** Migration 030 não foi executada

**Solução:**
```sql
-- Execute no SQL Editor do Supabase:
-- Arquivo: sql/030_fix_conversations_fk_to_users.sql
```

### ❌ Erro: "function match_knowledge_chunks does not exist"

**Causa:** Migration 029 não foi executada

**Solução:**
```sql
-- Execute no SQL Editor do Supabase:
-- Arquivo: sql/029_create_match_knowledge_chunks_function.sql
```

### ❌ "chunks_created": 0

**Causas possíveis:**
1. Nenhum registro em `knowledge_base` para esse `user_id`
2. Registros com campo `data` vazio ou inválido

**Debug:**
```sql
-- Verificar no Supabase:
SELECT * FROM knowledge_base WHERE user_id = 'uuid...';
```

### ⚠️ Sempre usa fallback

**Causa:** Tabela `knowledge_chunks` vazia

**Solução:**
```powershell
# Processar chunks primeiro:
curl.exe -X POST "http://localhost:8000/knowledge/process-chunks/{user_id}"
```

### ❌ OpenAI API error

**Causas:**
- `OPENAI_API_KEY` inválida ou expirada
- Sem créditos na conta OpenAI
- Rate limit excedido

**Verificar:**
```powershell
# Ver .env
cat .env | Select-String "OPENAI_API_KEY"

# Testar chave (PowerShell):
$headers = @{ "Authorization" = "Bearer $env:OPENAI_API_KEY" }
curl.exe -H $headers https://api.openai.com/v1/models
```

---

## Verificações de Sucesso

### ✅ Checklist

- [ ] Migration 030 executada (no erro de "usuarios")
- [ ] Migration 029 executada (função existe)
- [ ] `POST /knowledge/process-chunks` retorna `chunks_created > 0`
- [ ] Tabela `knowledge_chunks` tem registros no Supabase
- [ ] Logs mostram "Using vector search results"
- [ ] Chat responde perguntas semânticas corretamente

### 🎯 Teste Final

**Pergunta que NÃO está exatamente na base:**
```
"Posso experimentar antes de pagar?"
```

**Se vector search funciona:**
- Encontra chunks sobre "período de teste grátis" (similar concept)
- Responde: "Sim, oferecemos 30 dias de teste grátis"

**Se ainda usa busca antiga:**
- Pode não encontrar ou retornar resposta genérica

---

## Próximos Passos

### Automatizar processamento

Modificar endpoint de criação de knowledge:
```python
@app.post("/knowledge")
async def create_knowledge(data: KnowledgeCreate):
    # Salvar em knowledge_base
    result = save_to_kb(data)
    
    # Processar chunks automaticamente
    await process_knowledge_chunks(data.user_id)
    
    return result
```

### Monitorar custos

OpenAI Embeddings: ~$0.00002 / 1K tokens

**Exemplo:**
- 100 KB entries = ~$0.001
- 1000 queries/dia = ~$0.02/dia
- Custo mensal: ~$0.60

### Melhorar relevância

1. **Ajustar threshold:**
   ```python
   similarity_threshold=0.75  # Mais restritivo
   ```

2. **Aumentar chunks retornados:**
   ```python
   top_k=10  # Mais contexto
   ```

3. **Adicionar reranking** (futuro)

---

## Recursos

- 📚 [Documentação Completa](DOCS_RAG_VECTOR_IMPLEMENTATION.md)
- 🧪 [Test Script](test_rag_implementation.py)
- 🔄 [E2E Test](test_rag_e2e.py)
- 🗄️ [Migrations SQL](sql/)

**Implementado por:** GitHub Copilot  
**Data:** 18/11/2025

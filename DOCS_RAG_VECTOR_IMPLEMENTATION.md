# RAG-E com Embeddings Vetoriais - Guia de Implementação

## 📋 Visão Geral

Este documento descreve a implementação completa do sistema RAG (Retrieval-Augmented Generation) usando embeddings vetoriais para busca semântica na base de conhecimento.

### O que mudou?

**ANTES (Busca Textual Simples):**
- `get_context()` buscava **todos** os registros da tabela `knowledge_base`
- Filtro apenas por `user_id` e opcionalmente `category`
- Sem relevância semântica - retornava tudo

**AGORA (Busca Semântica com Vetores):**
- `hybrid_search()` usa **embeddings** para encontrar chunks **mais relevantes**
- Busca baseada na **pergunta do usuário** (semantic similarity)
- Retorna apenas **TOP-K** chunks mais similares
- **Fallback automático** para busca antiga se não houver chunks processados

---

## 🏗️ Arquitetura

```
Usuário faz pergunta
    ↓
1. Gera embedding da pergunta (OpenAI API)
    ↓
2. Busca vetorial em knowledge_chunks (pgvector)
    ↓
3. Retorna TOP-5 chunks mais similares
    ↓
4. Monta contexto com os chunks
    ↓
5. Envia para LLM (GPT-4) com contexto
    ↓
Resposta contextualizada
```

---

## 📦 Estrutura de Arquivos Criados

### Backend Services

1. **`src/services/embeddings.py`**
   - `generate_embedding(text)` - Gera embedding de um texto
   - `generate_embeddings_batch(texts)` - Gera embeddings em lote (até 2048 textos)
   - Usa modelo `text-embedding-3-small` (1536 dimensões)

2. **`src/services/chunking.py`**
   - `split_into_chunks(text, chunk_size=500, overlap=100)` - Divide texto em chunks
   - `prepare_knowledge_for_chunking(entry)` - Formata dados da KB para chunking
   - Quebra inteligente em fim de sentença

3. **`src/services/vector_search.py`**
   - `search_similar_chunks(user_id, query, top_k=5)` - Busca semântica
   - `get_context_from_chunks()` - Substitui `get_context()` original
   - `hybrid_search()` - Busca vetorial com fallback automático

### SQL Migrations

4. **`sql/029_create_match_knowledge_chunks_function.sql`**
   - Função PostgreSQL para busca vetorial
   - Usa pgvector com índice HNSW
   - Retorna chunks ordenados por similaridade

5. **`sql/030_fix_conversations_fk_to_users.sql`**
   - Corrige foreign key `usuarios` → `users`
   - Necessário executar ANTES de testar

### API Endpoints

6. **`POST /knowledge/process-chunks/{user_id}`**
   - Processa toda a base de conhecimento do usuário
   - Divide em chunks, gera embeddings, salva em `knowledge_chunks`
   - Retorna estatísticas de processamento

---

## 🗄️ Estrutura do Banco de Dados

### Tabela `knowledge_chunks` (já criada no migration 028)

```sql
CREATE TABLE knowledge_chunks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid NOT NULL,           -- FK para users
  knowledge_id uuid,                -- FK para knowledge_base.id
  category text,                    -- 'product', 'service', 'company', 'faq'
  source text,                      -- 'dashboard', 'api', 'manual.pdf'
  chunk_text text NOT NULL,         -- texto do chunk
  embedding vector(1536) NOT NULL,  -- vetor OpenAI
  created_at timestamptz DEFAULT NOW(),
  updated_at timestamptz DEFAULT NOW()
);

-- Índice HNSW para busca vetorial super rápida
CREATE INDEX idx_knowledge_chunks_embedding
  ON knowledge_chunks
  USING hnsw (embedding vector_cosine_ops);
```

### Função `match_knowledge_chunks()`

```sql
SELECT * FROM match_knowledge_chunks(
  query_embedding := '[0.1, 0.2, ...]'::vector(1536),
  match_count := 5,
  filter_user_id := 'uuid...',
  filter_category := 'product',
  similarity_threshold := 0.7
);
```

Retorna:
- `id`, `owner_id`, `knowledge_id`, `category`, `source`
- `chunk_text` - Texto do chunk
- `similarity` - Score de 0 a 1 (1 = idêntico)

---

## 🚀 Fluxo de Uso

### 1. Processar Base de Conhecimento

Após o usuário cadastrar conhecimento no painel, processar em chunks:

```bash
POST http://localhost:8000/knowledge/process-chunks/{user_id}
```

**Response:**
```json
{
  "message": "Chunks processados e embeddings gerados com sucesso",
  "knowledge_entries": 5,
  "chunks_created": 23,
  "processing_time_ms": 1847
}
```

**O que acontece:**
1. Busca todos os `knowledge_base` entries do user
2. Limpa chunks antigos (reprocessa tudo)
3. Para cada entry:
   - Formata texto usando `prepare_knowledge_for_chunking()`
   - Divide em chunks de 500 chars com overlap de 100
4. Gera embeddings em batch (OpenAI API)
5. Salva tudo em `knowledge_chunks`

### 2. Chat com Busca Semântica

O endpoint `/chat` agora usa automaticamente busca vetorial:

```bash
POST http://localhost:8000/chat
Content-Type: application/json

{
  "user_id": "uuid...",
  "message": "O plano Essential tem período de teste grátis?"
}
```

**Fluxo interno:**
1. `hybrid_search()` é chamado com a pergunta do usuário
2. Gera embedding da pergunta
3. Busca TOP-5 chunks mais similares
4. Se encontrar chunks → usa busca vetorial
5. Se não encontrar → fallback para `get_context()` original
6. Monta contexto e envia para LLM

**Resposta:**
```json
{
  "reply": "Sim! O plano Essential oferece 30 dias de teste grátis, sem necessidade de cartão de crédito.",
  "source": "ai_generated",
  "request_id": "..."
}
```

---

## 🔧 Configuração Necessária

### 1. Executar Migrations no Supabase

**IMPORTANTE:** Execute nesta ordem:

```sql
-- 1. Corrigir foreign keys (CRÍTICO)
-- Execute: sql/030_fix_conversations_fk_to_users.sql

-- 2. Criar função de busca vetorial
-- Execute: sql/029_create_match_knowledge_chunks_function.sql
```

### 2. Variáveis de Ambiente

Certifique-se que `.env` tem:

```env
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...supabase.co
SUPABASE_KEY=eyJ...
```

### 3. Dependências Python

Já instaladas em `requirements.txt`:
- `openai==1.40.2` ✅
- `supabase==2.9.0` ✅ (inclui pgvector support)

---

## 📊 Custo e Performance

### Custo de Embeddings (OpenAI)

**Modelo:** `text-embedding-3-small` (1536 dims)
**Preço:** ~$0.00002 / 1K tokens

**Exemplo:**
- 100 KB entries com ~500 palavras cada = 50K palavras
- Dividido em chunks de ~75 palavras = ~667 chunks
- Custo: ~$0.001 (menos de 1 centavo!)

### Performance

**Busca vetorial com HNSW:**
- Milhares de vetores: < 10ms
- Dezenas de milhares: < 50ms
- Centenas de milhares: < 100ms

**Embedding generation:**
- 1 texto: ~200ms
- 100 textos (batch): ~1.5s
- 1000 textos (batch): ~12s

---

## 🧪 Como Testar

### Teste 1: Processar Conhecimento

```powershell
# Substitua USER_ID pelo UUID real
$USER_ID = "e35af3a4-a7e6-422f-a483-bbcfc9d7c24f"

curl.exe -X POST "http://localhost:8000/knowledge/process-chunks/$USER_ID"
```

**Verifique:**
- Response com `chunks_created > 0`
- Logs: `"Generated X embeddings in batch"`
- Supabase: tabela `knowledge_chunks` tem registros

### Teste 2: Chat com Busca Semântica

```powershell
curl.exe -X POST http://localhost:8000/simulation/chat `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":\"e35af3a4-a7e6-422f-a483-bbcfc9d7c24f\",\"message\":\"Quanto custa o plano mais barato?\"}'
```

**Verifique:**
- Resposta menciona plano correto
- Logs: `"Using vector search results"` ou `"falling back to original"`
- Contexto inclui chunks relevantes

### Teste 3: Comparar Qualidade

**Pergunta ambígua:**
- "Tem desconto?" (sem especificar plano)

**Antes (busca antiga):**
- Retornava TODA a base de conhecimento
- LLM tinha que filtrar manualmente

**Agora (busca vetorial):**
- Retorna apenas chunks sobre "desconto"
- Resposta mais precisa e rápida

---

## 🔄 Migração Gradual (Hybrid Search)

O sistema usa **hybrid_search()** que:

1. **Tenta busca vetorial primeiro**
   - Se `knowledge_chunks` tem dados → usa vector search
   - Retorna TOP-5 chunks mais relevantes

2. **Fallback automático**
   - Se `knowledge_chunks` vazio → usa `get_context()` original
   - Garante que nada quebra durante a migração

3. **Zero impacto no frontend**
   - Frontend continua igual
   - Apenas precisa chamar `/knowledge/process-chunks` após cadastrar

---

## 📈 Próximos Passos (Opcional)

### 1. Processamento Automático
```python
# Em vez de chamar manualmente, processar automaticamente
# quando usuário salva na knowledge_base

@app.post("/knowledge")
async def create_knowledge(data: KnowledgeCreate):
    # Salva no knowledge_base
    result = save_knowledge(data)
    
    # Processa em background
    import asyncio
    asyncio.create_task(process_knowledge_chunks(data.user_id))
    
    return result
```

### 2. Processamento Incremental
```python
# Em vez de reprocessar tudo, processar apenas novos entries
# Adicionar campo `processed_at` em knowledge_base
```

### 3. Cache de Embeddings
```python
# Cachear embeddings de queries comuns
# Evita chamar OpenAI API para mesma pergunta
```

### 4. Reranking
```python
# Após busca vetorial, reordenar com modelo cross-encoder
# Melhora ainda mais a relevância
```

### 5. Multi-modal
```python
# Embeddings de imagens (CLIP)
# Busca semântica em PDFs, imagens, etc.
```

---

## 🐛 Troubleshooting

### Erro: "relation usuarios does not exist"
**Causa:** Foreign key constraint ainda aponta para tabela antiga
**Solução:** Execute `sql/030_fix_conversations_fk_to_users.sql`

### Erro: "function match_knowledge_chunks does not exist"
**Causa:** Migration 029 não foi executada
**Solução:** Execute `sql/029_create_match_knowledge_chunks_function.sql`

### Chunks não sendo criados
**Causa:** `knowledge_base` entries vazios ou formato inválido
**Debug:** Veja logs: `"Created X chunks from Y entries"`

### Busca sempre usa fallback
**Causa:** Tabela `knowledge_chunks` vazia
**Solução:** Rode `/knowledge/process-chunks/{user_id}` primeiro

### Embedding generation timeout
**Causa:** Muitos textos em um batch
**Solução:** Código já divide em chunks de 2048 automaticamente

---

## ✅ Checklist de Deploy

- [ ] Executar `sql/030_fix_conversations_fk_to_users.sql` no Supabase
- [ ] Executar `sql/029_create_match_knowledge_chunks_function.sql` no Supabase
- [ ] Verificar `OPENAI_API_KEY` no `.env`
- [ ] Reiniciar servidor FastAPI
- [ ] Processar chunks: `POST /knowledge/process-chunks/{user_id}`
- [ ] Testar chat: `POST /simulation/chat`
- [ ] Verificar logs para `"Using vector search results"`
- [ ] Comparar qualidade das respostas

---

## 📚 Referências

- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Supabase Vector Search](https://supabase.com/docs/guides/ai/vector-columns)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

**Implementado por:** GitHub Copilot  
**Data:** 18/11/2025  
**Versão:** 2.0.0 - RAG with Vector Embeddings

# 🛠 Documento Técnico — Chatbot IA no WhatsApp

## 📚 Visão Geral
Este projeto implementa um **chatbot de IA** integrado ao **WhatsApp Cloud API** e **OpenAI GPT**, com arquitetura orientada a serviços, persistência de contexto em **Redis** e práticas de segurança para produção.

A aplicação é executada no **Render** usando **Docker + Gunicorn**, com variáveis de ambiente para configuração, e preparada para escalabilidade horizontal.

---

## 📂 Estrutura de Serviços

### 1. `main.py` — **Ponto de Entrada da Aplicação**
- **Objetivo:** Gerenciar o servidor HTTP (Flask) que recebe eventos do WhatsApp.
- **Funções-chave:**
  - **`GET /webhook`** → validação inicial com `VERIFY_TOKEN`.
  - **`POST /webhook`** → recebe mensagens, valida assinatura `X-Hub-Signature-256`, aciona processamento assíncrono via thread.
- **Por que assim:** ACK imediato evita retries do Meta e mantém a latência baixa.

---

### 2. `src/core/bot_engine.py` — **Orquestrador Principal**
- **Objetivo:** Processar eventos recebidos e coordenar entre serviços.
- **Responsabilidades:**
  - **Verificação de assinatura** (`APP_SECRET`).
  - **Idempotência** por `message_id` (TTL configurável).
  - **Histórico de conversa** (via `KVStore` → Redis ou in-memory).
  - **Interpretação de tipos de mensagem** (texto, `interactive`).
  - **Chamada ao `AIService`** com histórico completo.
  - **Envio de resposta** via `WhatsAppService`.
- **Por que assim:** Centraliza lógica de negócio, isolando detalhes de integração.

---

### 3. `src/services/whatsapp_service.py` — **Integração com WhatsApp Cloud API**
- **Objetivo:** Encapsular toda comunicação com a API Graph do WhatsApp.
- **Recursos implementados:**
  - Uso de `requests.Session()` para conexões persistentes.
  - **Timeouts** e **retries exponenciais** para erros 429/5xx.
  - **Versão da API parametrizada** (`FB_GRAPH_VERSION`).
  - Envio de mensagens de texto.
- **Por que assim:** Garante resiliência e facilidade de manutenção/upgrade da API.

---

### 4. `src/services/ai_service.py` — **Integração com OpenAI GPT**
- **Objetivo:** Gerar respostas usando GPT com base no contexto.
- **Recursos implementados:**
  - Uso do cliente oficial `openai` (`OpenAI()`).
  - **Modelo e temperatura configuráveis** via env vars.
  - **Fallback de resposta** amigável em caso de erro.
  - Recebe histórico (`messages`) com `system`, `user`, `assistant`.
- **Por que assim:** Permite controle de criatividade e garante que o bot mantenha o tom desejado.

---

### 5. `src/utils/config.py` — **Configuração Centralizada**
- **Objetivo:** Unificar carregamento e acesso a variáveis de ambiente.
- **Recursos implementados:**
  - `load_dotenv()` único.
  - Variáveis para serviços (WhatsApp, OpenAI, Redis).
  - Variáveis de comportamento (histórico, idempotência, retries, timeout).
- **Por que assim:** Evita configuração espalhada pelo código, facilita manutenção.

---

### 6. `src/utils/kv_store.py` — **Armazenamento de Estado**
- **Objetivo:** Fornecer API simples para armazenamento de chave-valor.
- **Recursos implementados:**
  - **Backend Redis** (se `REDIS_URL` disponível e conexão bem-sucedida).
  - **Fallback in-memory** quando Redis indisponível.
  - Operações implementadas:
    - `set_idempotency(message_id, ttl)`
    - `seen(message_id)` → verifica duplicidade
    - `push_history(user, message_json, max_len)` → adiciona histórico
    - `get_history(user, limit)` → lê histórico
- **Por que assim:** Abstrai o armazenamento, permitindo mudar backend sem alterar lógica.

---

## 🔒 Segurança Implementada
- **Assinatura HMAC (`X-Hub-Signature-256`)** validada com `APP_SECRET`.
- **Tokens e chaves** sempre em variáveis de ambiente (nunca no código).
- **Idempotência** para evitar reprocessar mensagens.
- **Logs mascarados** (telefone do usuário não aparece em claro).

---

## 🧠 Histórico e Contexto
- **Onde:** Redis (`hist:<from_number>`) ou fallback in-memory.
- **Controle:** `MAX_HISTORY_MESSAGES` define profundidade.
- **Formato:** lista de JSONs `{role: "...", content: "..."}`.
- **Uso:** Enviado ao GPT junto com `SYSTEM_PROMPT` e mensagem atual.
- **Benefício:** Respostas contextuais e mais humanas.

---

## 🎨 Temperatura (`OPENAI_TEMPERATURE`)
- **Função:** Controla criatividade/aleatoriedade do GPT.
- **Faixas típicas:**
  - 0.0–0.3 → Respostas objetivas, consistentes.
  - 0.4–0.7 → Equilíbrio entre precisão e naturalidade.
  - 0.8+ → Criatividade alta, mas com risco de fuga de contexto.
- **Ajuste:** Simples troca de variável no `.env` sem redeploy de código.

---

## ⚙ Fluxo de Processamento

1. WhatsApp envia evento → `POST /webhook`.
2. `main.py` valida assinatura e dispara thread para `BotEngine`.
3. `BotEngine` verifica idempotência → busca histórico no `KVStore`.
4. Adiciona mensagem atual ao histórico → chama `AIService`.
5. `AIService` envia contexto ao GPT → retorna resposta.
6. `BotEngine` grava resposta no histórico → `WhatsAppService` envia ao usuário.

---

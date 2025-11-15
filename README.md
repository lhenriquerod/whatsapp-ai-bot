# 🤖 RAG-E Chat Service

## 📚 Visão Geral
Microserviço HTTP FastAPI que expõe endpoint `/chat` para integração com n8n. O serviço utiliza **OpenAI GPT** para gerar respostas baseadas em contexto armazenado no **Supabase** (knowledge base).

A aplicação é stateless, focada em performance e escalabilidade, ideal para arquiteturas de microserviços e orquestração via n8n.

---

## 🎯 Funcionalidades

- ✅ **Endpoint `/chat`** — POST com `user_id` e `message`, retorna resposta da IA
- ✅ **Endpoint `/simulation/chat`** — POST para testar agente sem WhatsApp (modo simulação)
- ✅ **Endpoint `/healthz`** — GET para health checks
- ✅ **Endpoints `/conversations/upsert` e `/messages`** — Integração com n8n para rastreamento
- ✅ **RAG (Retrieval-Augmented Generation)** — busca contexto no Supabase antes de gerar resposta
- ✅ **Personalidade do Agente** — configuração completa de tom de voz, nível de formalidade e comportamento
- ✅ **Base de Conhecimento Flexível** — suporte a produtos com múltiplos planos, FAQs, serviços e informações da empresa
- ✅ **OpenAI GPT** — respostas naturais e contextualizadas
- ✅ **CORS configurável** — preparado para produção
- ✅ **Logs estruturados** — request_id, latência, mascaramento de PII
- ✅ **Docker ready** — containerização com uvicorn
- ✅ **Validação Pydantic** — tipo seguro em requests/responses

---

## 📂 Estrutura do Projeto

```
.
├── app.py                            # FastAPI app com rotas /chat e /healthz
├── src/
│   ├── services/
│   │   ├── ai_service.py            # Cliente OpenAI (GPT)
│   │   ├── supabase_service.py      # Cliente Supabase + get_context()
│   │   ├── personality_service.py   # Gerenciamento de personalidade do agente
│   │   ├── conversation_service.py  # Serviços de conversação
│   │   └── message_service.py       # Serviços de mensagens
│   ├── models/
│   │   ├── conversation.py          # Modelos de conversação
│   │   └── message.py               # Modelos de mensagens
│   └── utils/
│       ├── __init__.py
│       └── config.py                # Configuração de variáveis de ambiente
├── requirements.txt                  # Dependências Python
├── Dockerfile                        # Container configuration
├── README.md                         # Este arquivo
├── DOCS_PERSONALIDADE_AGENTE.md     # Documentação completa sobre personalidade
└── test_personality_integration.py  # Script de teste de integração
```

---

## 🔧 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Server
PORT=8000

# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sua_service_role_key  # Use service role para backend!
# SUPABASE_ANON_KEY=sua_anon_key  # Opcional, apenas se não usar service role

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2

# Knowledge Base (Supabase table base_conhecimento)
KB_TABLE=base_conhecimento
KB_OWNER_COL=user_id
KB_FIELDS=categoria,dados
KB_LIMIT=10
```

### Descrição das Variáveis:

| Variável | Descrição | Default |
|----------|-----------|---------|
| `PORT` | Porta do servidor | `8000` |
| `SUPABASE_URL` | URL do projeto Supabase | obrigatório |
| `SUPABASE_SERVICE_ROLE_KEY` | **Service Role Key** do Supabase (bypassa RLS) | obrigatório |
| `SUPABASE_ANON_KEY` | Chave pública (fallback se service role não definida) | opcional |
| `OPENAI_API_KEY` | Chave da API OpenAI | obrigatório |
| `OPENAI_MODEL` | Modelo GPT a ser usado | `gpt-4o-mini` |
| `OPENAI_TEMPERATURE` | Criatividade (0.0-1.0) | `0.2` |
| `KB_TABLE` | Nome da tabela no Supabase | `base_conhecimento` |
| `KB_OWNER_COL` | Coluna de identificação do dono | `user_id` |
| `KB_FIELDS` | Campos a buscar (separados por vírgula) | `categoria,dados` |
| `KB_LIMIT` | Limite de registros a buscar | `10` |

> ⚠️ **Importante**: Para backend services, sempre use `SUPABASE_SERVICE_ROLE_KEY` em vez de `SUPABASE_ANON_KEY`. A service role key bypassa Row-Level Security (RLS) policies, permitindo operações administrativas necessárias para o microserviço.

---

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.10+
- Conta Supabase com tabela de knowledge base configurada
- Chave API OpenAI

### Instalação local

```bash
# Clone o repositório
git clone https://github.com/lhenriquerod/whatsapp-ai-bot.git
cd whatsapp-ai-bot

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure .env (copie e edite)
cp .env.example .env  # edite com suas credenciais

# Execute o servidor
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Execução com Docker

```bash
# Build da imagem
docker build -t rag-e-chat .

# Execute o container
docker run -p 8000:8000 --env-file .env rag-e-chat
```

---

## 📡 API Reference

### `GET /healthz`
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

---

### `POST /chat`
Processa mensagem do usuário e retorna resposta da IA baseada no conhecimento do Supabase.

**Headers (opcionais):**
- `X-Request-Id`: ID para rastreamento de requisição

**Request Body:**
```json
{
  "user_id": "user_123",
  "message": "Qual o horário de atendimento?"
}
```

**Response:**
```json
{
  "reply": "Nosso horário de atendimento é de segunda a sexta, das 9h às 18h.",
  "source": "supabase",
  "request_id": "abc-123"
}
```

**Códigos de Status:**
- `200` — Sucesso
- `422` — Validação falhou (campos obrigatórios ausentes)
- `500` — Erro interno (problema com Supabase ou OpenAI)

---

### `POST /simulation/chat`
Endpoint para testar o agente sem integração WhatsApp (modo simulação do painel web).

**Diferenças do `/chat`:**
- Usa configurações personalizadas do usuário (tom de voz, personalidade)
- NÃO cria registros em `conversas` ou `mensagens`
- Ideal para testar o agente antes de colocar em produção

**Headers (opcionais):**
- `X-Request-Id`: ID para rastreamento de requisição

**Request Body:**
```json
{
  "user_id": "6bf0dab0-e895-4730-b5fa-cd8acff6de0c",
  "message": "Olá, quero testar meu agente."
}
```

**Response:**
```json
{
  "reply": "Olá! Aqui é o agente em modo simulação. Como posso ajudá-lo?",
  "source": "supabase",
  "request_id": "test-123"
}
```

**Códigos de Status:**
- `200` — Sucesso
- `422` — Validação falhou
- `500` — Erro interno

---

## 🎭 Personalidade do Agente

O RAG-E suporta configuração completa da personalidade do agente através da tabela `personalidade_agente` no Supabase.

### Configurações Disponíveis

| Campo | Tipo | Valores | Descrição |
|-------|------|---------|-----------|
| `nome` | string | Qualquer | Nome do assistente (ex: "RAG-E Assistant") |
| `nivel_personalidade` | int | 1-10 | Nível de formalidade/casualidade |
| `tom_voz` | string | formal, amigavel, objetivo, descontraido | Estilo de comunicação |
| `forma_tratamento` | string | voce, senhor, informal | Como tratar o cliente |
| `apresentacao_inicial` | text | Qualquer | Mensagem de boas-vindas |

### Níveis de Personalidade

- **1-3**: Extremamente formal até levemente formal
- **4-6**: Equilibrado (profissional e amigável)
- **7-9**: Casual até muito entusiasmado
- **10**: Técnico e especialista

### Exemplo de Uso

```python
from src.services.personality_service import get_agent_personality

# Buscar personalidade do usuário
personality = get_agent_personality("user-id-aqui")

# Retorna:
{
    "nome": "RAG-E Assistant",
    "nivel_personalidade": 7,
    "tom_voz": "amigavel",
    "forma_tratamento": "voce",
    "apresentacao_inicial": "Oi! Como posso ajudar? 😊"
}
```

### Fallback Automático

Se o usuário não tiver personalidade configurada, o sistema usa valores padrão:
- Nome: "Assistente Virtual"
- Nível: 5 (Equilibrado)
- Tom: "amigavel"
- Tratamento: "voce"

📖 **Documentação completa**: Veja [DOCS_PERSONALIDADE_AGENTE.md](./DOCS_PERSONALIDADE_AGENTE.md)

---

## 📚 Base de Conhecimento

O sistema suporta diferentes categorias de conhecimento na tabela `base_conhecimento`:

### Categorias Suportadas

#### 1. **Produto** (`categoria: "produto"`)
Suporta 5 tipos de produtos:
- `produto_unico`: Produto com preço único
- `assinatura_plano_unico`: Assinatura com 1 plano
- `assinatura_multiplos_planos`: Assinatura com múltiplos planos (ex: Básico, Pro, Enterprise)
- `pacote_combo`: Pacote com vários itens inclusos
- `sob_consulta`: Produto sem preço fixo

**Exemplo - Produto com múltiplos planos:**
```json
{
  "nome": "RAG-E",
  "tipo_produto": "assinatura_multiplos_planos",
  "descricao": "Plataforma de IA para atendimento",
  "planos": [
    {
      "nome": "Essencial",
      "preco_mensal": "260",
      "preco_anual": "2600",
      "desconto_anual": "2 meses Grátis",
      "beneficios": ["IA WhatsApp", "Base de conhecimento"],
      "limite_usuarios": "5 usuários",
      "limite_conversas": "1000/mês",
      "ideal_para": "Pequenos negócios"
    }
  ]
}
```

#### 2. **FAQ** (`categoria: "faq"`)
```json
{
  "pergunta": "Qual o horário de atendimento?",
  "resposta": "Segunda a sexta, das 9h às 18h",
  "categoria_faq": "Atendimento"
}
```

#### 3. **Serviço** (`categoria: "servico"`)
```json
{
  "nome": "Consultoria em IA",
  "descricao": "Implementação de soluções de IA",
  "preco": "5000",
  "duracao": "3 meses"
}
```

#### 4. **Empresa** (`categoria: "empresa"`)
```json
{
  "tipo": "Sobre a empresa",
  "titulo": "Nossa Missão",
  "descricao": "Revolucionar atendimento com IA",
  "informacoes_adicionais": "Fundada em 2025"
}
```

#### 5. **Personalizado** (`categoria: "personalizado"`)
Conteúdo customizado com campos flexíveis.

📖 **Mais exemplos**: Veja [test_produto_com_planos.py](./test_produto_com_planos.py)

---

## 🧪 Teste Manual

### Com curl:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-Request-Id: test-123" \
  -d '{
    "user_id": "u_1",
    "message": "Quais são os horários de atendimento?"
  }'
```

### Com Python requests:

```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "user_id": "user_123",
        "message": "Como posso fazer um pedido?"
    },
    headers={"X-Request-Id": "test-456"}
)

print(response.json())
```

---

## 🗄️ Configuração do Supabase

### Estrutura da Tabela (exemplo)

Crie uma tabela `base_conhecimento` no Supabase (veja RELATORIO_ESTRUTURA_BD.md para detalhes completos):

```sql
CREATE TABLE base_conhecimento (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  categoria VARCHAR(50) NOT NULL CHECK (categoria IN ('produto', 'servico', 'empresa', 'faq', 'personalizado')),
  dados JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Adicione RLS (Row Level Security) para segurança
ALTER TABLE base_conhecimento ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own knowledge"
  ON base_conhecimento
  FOR ALL
  USING (user_id = auth.uid());

-- Índices para performance
CREATE INDEX idx_base_conhecimento_user_id ON base_conhecimento(user_id);
CREATE INDEX idx_base_conhecimento_categoria ON base_conhecimento(categoria);
CREATE INDEX idx_base_conhecimento_dados ON base_conhecimento USING GIN(dados);
```

### Exemplo de Dados:

```sql
-- FAQ
INSERT INTO base_conhecimento (user_id, categoria, dados) VALUES
  ('user_123', 'faq', '{"pergunta": "Qual o horário de atendimento?", "resposta": "Atendemos de segunda a sexta, das 9h às 18h."}');

-- Produto
INSERT INTO base_conhecimento (user_id, categoria, dados) VALUES
  ('user_123', 'produto', '{"nome": "Smartphone X", "descricao": "Celular top de linha", "preco": "R$ 2.999,90", "caracteristicas": "128GB, câmera 48MP"}');

-- Serviço
INSERT INTO base_conhecimento (user_id, categoria, dados) VALUES
  ('user_123', 'servico', '{"nome": "Consultoria", "descricao": "Consultoria em TI", "duracao": "2 horas", "preco": "R$ 500"}');

-- Empresa
INSERT INTO base_conhecimento (user_id, categoria, dados) VALUES
  ('user_123', 'empresa', '{"topico": "Missão", "conteudo": "Oferecer as melhores soluções em tecnologia"}');
```

---

## 🔗 Integração com n8n

### Fluxo Típico:

1. **Webhook Trigger** — Recebe mensagem do WhatsApp/Telegram/etc
2. **HTTP Request Node** → `POST http://seu-servico/chat`
   - Body: `{"user_id": "{{$json.from}}", "message": "{{$json.text}}"}`
3. **Respond to Webhook** — Retorna `{{$json.reply}}` para o usuário

### Exemplo de configuração HTTP Request Node:

```json
{
  "method": "POST",
  "url": "https://seu-dominio.com/chat",
  "authentication": "none",
  "body": {
    "user_id": "={{ $json.from }}",
    "message": "={{ $json.text }}"
  },
  "headers": {
    "Content-Type": "application/json",
    "X-Request-Id": "={{ $execution.id }}"
  }
}
```

---

## 🔒 Segurança

- ✅ **CORS**: Configure `allow_origins` no `app.py` para produção
- ✅ **RLS no Supabase**: Ative Row Level Security na tabela
- ✅ **Logs sem PII**: `user_id` é mascarado nos logs
- ✅ **HTTPS**: Use reverse proxy (nginx/Caddy) ou deploy em plataforma com SSL
- ✅ **Rate Limiting**: Considere adicionar middleware de rate limiting

---

## � Monitoramento e Logs

Os logs incluem:
- `chat_start` — Início do processamento
- `chat_success` — Resposta gerada com sucesso + latência
- `chat_error` — Erros com stack trace

Exemplo de log:
```
2025-11-07 10:30:45 INFO app - chat_start user=***5678 request_id=req-123
2025-11-07 10:30:47 INFO app - chat_success user=***5678 request_id=req-123 elapsed_ms=1842
```

---

## 🛠 Tecnologias Utilizadas

- **FastAPI** — Framework web moderno e rápido
- **Uvicorn** — ASGI server de alta performance
- **OpenAI GPT** — Modelo de linguagem para respostas
- **Supabase** — Backend-as-a-Service (PostgreSQL)
- **Pydantic** — Validação de dados
- **Docker** — Containerização

---

## 📝 Changelog

### v2.0.0 (2025-11-07)
- 🔄 **Refatoração completa**: de bot WhatsApp para microserviço HTTP
- ➕ Adicionado endpoint `/chat` com integração Supabase
- ➕ Adicionado RAG (Retrieval-Augmented Generation)
- ➖ Removido webhook WhatsApp e lógica Meta
- ➖ Removido Redis/idempotência
- 🔧 Migrado de Flask para FastAPI
- 🔧 Migrado de Gunicorn para Uvicorn

### v1.0.0 (2025-10-XX)
- 🎉 Versão inicial como bot WhatsApp

---

## 📄 Licença

MIT License — veja LICENSE para detalhes.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:
1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 👤 Autor

**Lucas Henrique**  
GitHub: [@lhenriquerod](https://github.com/lhenriquerod)

---

## 🙏 Agradecimentos

- OpenAI pela API GPT
- Supabase pelo excelente BaaS
- FastAPI pela framework incrível

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

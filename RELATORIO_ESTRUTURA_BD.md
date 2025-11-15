# 📊 Relatório de Estrutura do Banco de Dados - RAG-E

**Data:** 08 de Novembro de 2025  
**Sistema:** RAG-E - Plataforma de Agentes Conversacionais IA  
**Banco de Dados:** Supabase (PostgreSQL)

---

## 📑 Índice de Tabelas

1. [usuarios](#1-usuarios) - Informações estendidas dos usuários
2. [configuracao_empresa](#2-configuracao_empresa) - Configurações da empresa/agente
3. [base_conhecimento](#3-base_conhecimento) - Base de conhecimento do chatbot

---

## 1. `usuarios`

**Descrição:** Tabela que estende as informações dos usuários do sistema de autenticação do Supabase (auth.users), armazenando dados complementares e configurações de plano.

### Campos:

| Campo | Tipo | Restrições | Descrição |
|-------|------|------------|-----------|
| `id` | UUID | PRIMARY KEY, FK → auth.users(id) | Identificador único do usuário, referencia a tabela de autenticação |
| `nome` | VARCHAR(255) | NULL | Nome completo do usuário |
| `telefone` | VARCHAR(20) | NULL | Número de telefone do usuário para contato |
| `plano` | VARCHAR(50) | NOT NULL, DEFAULT 'Essencial' | Plano de assinatura: 'Essencial', 'Starter' ou 'Premium' |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'ativo' | Status da conta: 'ativo', 'inativo' ou 'suspenso' |
| `is_admin` | BOOLEAN | NOT NULL, DEFAULT FALSE | Flag que indica se o usuário possui privilégios de administrador |
| `total_conversas` | INTEGER | DEFAULT 0 | Contador total de conversas realizadas pelo agente do usuário |
| `ultimo_acesso` | TIMESTAMP WITH TIME ZONE | NULL | Data e hora do último acesso do usuário à plataforma |
| `data_cadastro` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Data e hora do cadastro inicial do usuário |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Data e hora de criação do registro |
| `updated_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Data e hora da última atualização do registro |

### Índices:
- `idx_usuarios_plano` - Otimiza buscas por plano
- `idx_usuarios_status` - Otimiza buscas por status
- `idx_usuarios_is_admin` - Otimiza buscas de administradores

### Políticas RLS (Row Level Security):
- Usuários podem ver e atualizar apenas seu próprio perfil
- Administradores podem ver e atualizar todos os perfis

### Triggers:
- **`on_auth_user_created`**: Cria automaticamente um registro em `usuarios` quando um novo usuário se registra no sistema
- **`update_usuarios_updated_at`**: Atualiza automaticamente o campo `updated_at` quando há modificações

---

## 2. `configuracao_empresa`

**Descrição:** Armazena as configurações personalizadas da empresa/negócio do usuário, que serão utilizadas para treinar e personalizar o agente conversacional.

### Campos:

| Campo | Tipo | Restrições | Descrição |
|-------|------|------------|-----------|
| `id` | UUID | PRIMARY KEY | Identificador único da configuração |
| `user_id` | UUID | NOT NULL, FK → auth.users(id), UNIQUE | Referência ao usuário (cada usuário tem apenas uma configuração) |
| `nome_empresa` | VARCHAR(200) | NOT NULL | Nome da empresa ou negócio |
| `ramo_atividade` | VARCHAR(200) | NOT NULL | Setor ou ramo de atividade da empresa (ex: "E-commerce", "Consultoria") |
| `servico_produto` | TEXT | NULL | Descrição detalhada dos produtos ou serviços oferecidos |
| `horario_funcionamento` | TEXT | NOT NULL | Horários de funcionamento (ex: "Seg-Sex 9h-18h, Sáb 9h-13h") |
| `politica_precos` | TEXT | NULL | Informações sobre preços, formas de pagamento e políticas comerciais |
| `diferenciais` | TEXT | NULL | Diferenciais competitivos e pontos fortes da empresa |
| `tom_voz` | VARCHAR(50) | DEFAULT 'amigavel' | Tom de voz do agente: 'formal', 'amigavel', 'objetivo' ou 'descontraido' |
| `webhook_url` | TEXT | NULL | URL do webhook n8n para integração com automações externas |
| `prompt_base_persona` | TEXT | NULL | Prompt personalizado que define a personalidade e comportamento do agente |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Data e hora de criação da configuração |
| `updated_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Data e hora da última atualização |

### Índices:
- `idx_configuracao_empresa_user_id` - Otimiza busca por usuário

### Políticas RLS:
- Usuários podem realizar CRUD completo apenas em sua própria configuração

### Triggers:
- **`update_configuracao_empresa_updated_at`**: Atualiza automaticamente o timestamp de modificação

### Observações:
- Constraint UNIQUE em `user_id` garante que cada usuário tenha apenas uma configuração ativa

---

## 3. `base_conhecimento`

**Descrição:** Armazena itens da base de conhecimento que o agente utilizará para responder perguntas. Suporta múltiplas categorias com estrutura de dados dinâmica usando JSONB.

### Campos:

| Campo | Tipo | Restrições | Descrição |
|-------|------|------------|-----------|
| `id` | UUID | PRIMARY KEY | Identificador único do item de conhecimento |
| `user_id` | UUID | NOT NULL, FK → auth.users(id) | Referência ao usuário proprietário do conhecimento |
| `categoria` | VARCHAR(50) | NOT NULL | Tipo de conhecimento: 'produto', 'servico', 'empresa', 'faq' ou 'personalizado' |
| `dados` | JSONB | NOT NULL | Estrutura de dados dinâmica que varia conforme a categoria (JSON flexível) |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Data e hora de criação do item |
| `updated_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Data e hora da última modificação |

### Índices:
- `idx_base_conhecimento_user_id` - Otimiza busca por usuário
- `idx_base_conhecimento_categoria` - Otimiza busca por categoria
- `idx_base_conhecimento_dados` (GIN) - Otimiza buscas dentro do campo JSONB

### Políticas RLS:
- Usuários podem realizar operações CRUD completo apenas em seus próprios itens de conhecimento

### Triggers:
- **`update_base_conhecimento_updated_at`**: Atualiza automaticamente o timestamp de modificação

### Estrutura do campo `dados` por categoria:

#### Categoria: `produto`
```json
{
  "nome": "Nome do Produto",
  "descricao": "Descrição detalhada",
  "preco": "R$ 99,90",
  "caracteristicas": "Lista de características"
}
```

#### Categoria: `servico`
```json
{
  "nome": "Nome do Serviço",
  "descricao": "O que o serviço oferece",
  "duracao": "Tempo estimado",
  "preco": "Valor do serviço"
}
```

#### Categoria: `empresa`
```json
{
  "topico": "Sobre a empresa",
  "conteudo": "História, missão, valores, etc."
}
```

#### Categoria: `faq`
```json
{
  "pergunta": "Pergunta frequente",
  "resposta": "Resposta detalhada"
}
```

#### Categoria: `personalizado`
```json
{
  // Estrutura livre definida pelo usuário
}
```

---

## 🔐 Segurança Implementada

### Row Level Security (RLS)
Todas as tabelas possuem RLS ativado, garantindo que:
- ✅ Usuários só podem acessar seus próprios dados
- ✅ Administradores (is_admin=true) têm acesso a todos os dados na tabela `usuarios`
- ✅ Proteção automática contra acesso não autorizado

### Triggers Automáticos
- ✅ Criação automática de registro em `usuarios` ao criar conta
- ✅ Atualização automática de timestamps em todas as modificações
- ✅ Tratamento de exceções para evitar falhas no signup

### Constraints
- ✅ CHECK constraints para validar valores permitidos (planos, status, categorias)
- ✅ Foreign Keys com CASCADE DELETE para manter integridade referencial
- ✅ UNIQUE constraints para evitar duplicação de dados

---

## 📈 Relacionamentos entre Tabelas

```
auth.users (Supabase Auth)
    ↓ (1:1)
usuarios ───────────────────────┐
    ↓ (1:1)                     │
configuracao_empresa            │
                                │ (1:N)
                                ↓
                        base_conhecimento
```

### Descrição dos Relacionamentos:

1. **auth.users → usuarios** (1:1)
   - Cada usuário autenticado tem exatamente um registro estendido

2. **usuarios → configuracao_empresa** (1:1)
   - Cada usuário possui uma única configuração de empresa

3. **usuarios → base_conhecimento** (1:N)
   - Cada usuário pode ter múltiplos itens na base de conhecimento

---

## 🛠️ Funções Auxiliares

### `update_updated_at_column()`
**Tipo:** TRIGGER FUNCTION  
**Descrição:** Atualiza automaticamente o campo `updated_at` com o timestamp atual sempre que um registro é modificado.

### `create_usuario_extended()`
**Tipo:** TRIGGER FUNCTION  
**Descrição:** Cria automaticamente um registro na tabela `usuarios` quando um novo usuário se registra no sistema de autenticação.  
**Segurança:** SECURITY DEFINER (executa com privilégios do criador)  
**Tratamento de Erros:** Possui exception handler para não bloquear o signup em caso de falha

---

## 📋 Scripts SQL Executados

1. ✅ `setup_usuarios_completo.sql` - Criação da tabela usuarios com triggers
2. ✅ `create_configuracao_empresa.sql` - Criação da tabela de configurações
3. ✅ `001_create_base_conhecimento.sql` - Criação da base de conhecimento
4. ✅ `confirmar_email.sql` - Confirmação manual de email para desenvolvimento

---

## 🎯 Próximas Tabelas a Implementar (Futuro)

Baseado na estrutura completa do projeto, ainda faltam:

1. **personalidade_agente** - Configurações detalhadas de personalidade
2. **conversas** - Cabeçalho das conversas
3. **mensagens** - Mensagens individuais das conversas
4. **transacoes** - Histórico financeiro
5. **Views e Functions** - Métricas administrativas e cálculo de MRR

---

**Observações Finais:**
- Todas as tabelas utilizam UUID como chave primária
- Timestamps incluem fuso horário (TIMESTAMP WITH TIME ZONE)
- Políticas RLS garantem isolamento de dados entre usuários
- Índices otimizados para as consultas mais frequentes


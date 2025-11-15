-- ============================================================================
-- Criação das Tabelas: conversas e messages
-- Para uso com RAG-E Chat Service
-- Execute este script no SQL Editor do Supabase
-- ============================================================================

-- Tabela: conversas
-- Descrição: Armazena conversas/threads entre usuários e contatos externos
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,  -- FK para auth.users se necessário
    external_contact_id TEXT NOT NULL,  -- ID externo (ex: WhatsApp ID)
    contact_name TEXT,
    source TEXT NOT NULL,  -- 'whatsapp', 'simulacao', etc.
    status TEXT NOT NULL DEFAULT 'open',  -- 'open', 'closed'
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraint: Uma conversa única por user_id e contact
    CONSTRAINT unique_user_contact UNIQUE (user_id, external_contact_id)
);

-- Comentários descritivos
COMMENT ON TABLE conversas IS 'Conversas/threads entre usuários e contatos externos (WhatsApp, etc)';
COMMENT ON COLUMN conversas.user_id IS 'Identificador do usuário/tenant dono da conversa';
COMMENT ON COLUMN conversas.external_contact_id IS 'ID externo do contato (ex: número WhatsApp)';
COMMENT ON COLUMN conversas.source IS 'Origem da conversa: whatsapp, simulacao, etc';
COMMENT ON COLUMN conversas.status IS 'Status da conversa: open, closed';

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_conversas_user_id ON conversas(user_id);
CREATE INDEX IF NOT EXISTS idx_conversas_external_contact ON conversas(external_contact_id);
CREATE INDEX IF NOT EXISTS idx_conversas_status ON conversas(status);
CREATE INDEX IF NOT EXISTS idx_conversas_source ON conversas(source);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_conversas_updated_at ON conversas;
CREATE TRIGGER update_conversas_updated_at
    BEFORE UPDATE ON conversas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- Tabela: messages
-- Descrição: Armazena mensagens individuais de cada conversa
-- ============================================================================

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversas(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,  -- Duplicado para facilitar queries
    external_contact_id TEXT NOT NULL,  -- Duplicado para facilitar queries
    direction TEXT NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    type TEXT NOT NULL,  -- 'user', 'assistant', 'system', etc
    text TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB,  -- Dados adicionais flexíveis
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Comentários descritivos
COMMENT ON TABLE messages IS 'Mensagens individuais de conversas';
COMMENT ON COLUMN messages.conversation_id IS 'Referência à conversa pai';
COMMENT ON COLUMN messages.direction IS 'Direção: inbound (recebida) ou outbound (enviada)';
COMMENT ON COLUMN messages.type IS 'Tipo de mensagem: user, assistant, system';
COMMENT ON COLUMN messages.metadata IS 'Metadados adicionais em formato JSON';

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_external_contact ON messages(external_contact_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_messages_direction ON messages(direction);
CREATE INDEX IF NOT EXISTS idx_messages_type ON messages(type);

-- Índice GIN para busca em metadata JSONB
CREATE INDEX IF NOT EXISTS idx_messages_metadata ON messages USING GIN(metadata);


-- ============================================================================
-- Row Level Security (RLS) - OPCIONAL
-- Descomente se quiser ativar segurança por linha
-- ============================================================================

-- Ativar RLS nas tabelas
-- ALTER TABLE conversas ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Política: Usuários só veem suas próprias conversas
-- CREATE POLICY "Users can view own conversations"
--     ON conversas
--     FOR SELECT
--     USING (user_id = auth.uid());

-- Política: Usuários só podem inserir em suas próprias conversas
-- CREATE POLICY "Users can insert own conversations"
--     ON conversas
--     FOR INSERT
--     WITH CHECK (user_id = auth.uid());

-- Política: Usuários só podem atualizar suas próprias conversas
-- CREATE POLICY "Users can update own conversations"
--     ON conversas
--     FOR UPDATE
--     USING (user_id = auth.uid());

-- Política: Usuários só veem suas próprias mensagens
-- CREATE POLICY "Users can view own messages"
--     ON messages
--     FOR SELECT
--     USING (user_id = auth.uid());

-- Política: Usuários só podem inserir em suas próprias mensagens
-- CREATE POLICY "Users can insert own messages"
--     ON messages
--     FOR INSERT
--     WITH CHECK (user_id = auth.uid());


-- ============================================================================
-- Dados de Teste (OPCIONAL)
-- Descomente para inserir dados de exemplo
-- ============================================================================

-- INSERT INTO conversas (user_id, external_contact_id, contact_name, source, status) VALUES
--     ('123e4567-e89b-12d3-a456-426614174000', '5511999887766', 'João Silva', 'whatsapp', 'open'),
--     ('123e4567-e89b-12d3-a456-426614174000', '5511988776655', 'Maria Santos', 'whatsapp', 'open');

-- INSERT INTO messages (conversation_id, user_id, external_contact_id, direction, type, text, metadata) VALUES
--     (
--         (SELECT id FROM conversas WHERE external_contact_id = '5511999887766' LIMIT 1),
--         '123e4567-e89b-12d3-a456-426614174000',
--         '5511999887766',
--         'inbound',
--         'user',
--         'Olá! Gostaria de saber o horário de funcionamento.',
--         '{"whatsapp_message_id": "wamid.xxx", "phone_number": "5511999887766"}'::jsonb
--     ),
--     (
--         (SELECT id FROM conversas WHERE external_contact_id = '5511999887766' LIMIT 1),
--         '123e4567-e89b-12d3-a456-426614174000',
--         '5511999887766',
--         'outbound',
--         'assistant',
--         'Nosso horário é de segunda a sexta, das 9h às 18h.',
--         '{}'::jsonb
--     );


-- ============================================================================
-- Verificação da Estrutura
-- ============================================================================

-- Verificar se as tabelas foram criadas
SELECT 
    table_name, 
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('conversas', 'messages')
ORDER BY table_name;

-- Verificar constraints
SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'public'
  AND tc.table_name IN ('conversas', 'messages')
ORDER BY tc.table_name, tc.constraint_type;

-- Verificar índices
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('conversas', 'messages')
ORDER BY tablename, indexname;


-- ============================================================================
-- Script concluído!
-- ============================================================================

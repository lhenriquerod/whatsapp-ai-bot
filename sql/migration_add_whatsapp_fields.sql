-- ============================================================================
-- Script de Migração: Adicionar campos necessários para integração WhatsApp
-- Execute no SQL Editor do Supabase
-- ============================================================================

-- Adicionar campos à tabela conversas
ALTER TABLE conversas 
ADD COLUMN IF NOT EXISTS external_contact_id TEXT,
ADD COLUMN IF NOT EXISTS contact_name TEXT,
ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'whatsapp';

-- Migrar dados existentes (se houver)
UPDATE conversas 
SET contact_name = titulo 
WHERE contact_name IS NULL AND titulo IS NOT NULL;

-- Criar índices para os novos campos
CREATE INDEX IF NOT EXISTS idx_conversas_external_contact ON conversas(external_contact_id);
CREATE INDEX IF NOT EXISTS idx_conversas_source ON conversas(source);

-- Criar constraint único para evitar conversas duplicadas por contato
-- CUIDADO: Só execute se não houver duplicatas
-- ALTER TABLE conversas 
-- ADD CONSTRAINT unique_user_contact UNIQUE (user_id, external_contact_id);

-- Adicionar campos à tabela mensagens
ALTER TABLE mensagens
ADD COLUMN IF NOT EXISTS direction TEXT,
ADD COLUMN IF NOT EXISTS external_contact_id TEXT,
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMPTZ DEFAULT NOW();

-- Migrar tipo para direction (baseado no tipo existente)
UPDATE mensagens
SET direction = CASE 
    WHEN tipo = 'usuario' THEN 'inbound'
    WHEN tipo = 'agente' THEN 'outbound'
    ELSE 'inbound'
END
WHERE direction IS NULL;

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_mensagens_direction ON mensagens(direction);
CREATE INDEX IF NOT EXISTS idx_mensagens_external_contact ON mensagens(external_contact_id);
CREATE INDEX IF NOT EXISTS idx_mensagens_timestamp ON mensagens(timestamp DESC);

-- Comentários descritivos
COMMENT ON COLUMN conversas.external_contact_id IS 'ID externo do contato (ex: número WhatsApp)';
COMMENT ON COLUMN conversas.source IS 'Origem da conversa: whatsapp, simulacao, etc';
COMMENT ON COLUMN mensagens.direction IS 'Direção: inbound (recebida) ou outbound (enviada)';

-- ============================================================================
-- Verificação
-- ============================================================================

-- Ver estrutura da tabela conversas
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'conversas'
ORDER BY ordinal_position;

-- Ver estrutura da tabela mensagens
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'mensagens'
ORDER BY ordinal_position;

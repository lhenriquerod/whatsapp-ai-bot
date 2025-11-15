-- ============================================================================
-- Script para corrigir constraint de status na tabela conversas
-- Execute este SQL no Supabase SQL Editor
-- ============================================================================

-- 1. Remover a constraint problemática atual
ALTER TABLE conversas 
DROP CONSTRAINT IF EXISTS conversas_status_chk;

ALTER TABLE conversas 
DROP CONSTRAINT IF EXISTS conversas_status_check;

-- 2. Alterar o valor DEFAULT para 'ativa' (em vez de 'aberta')
ALTER TABLE conversas 
ALTER COLUMN status SET DEFAULT 'ativa';

-- 3. Criar nova constraint com valores corretos
ALTER TABLE conversas
ADD CONSTRAINT conversas_status_check 
CHECK (status IN ('ativa', 'pendente', 'finalizada', 'cancelada', 'arquivada'));

-- 4. Verificar a nova constraint
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
WHERE rel.relname = 'conversas' 
  AND con.contype = 'c'
  AND conname LIKE '%status%';

-- ============================================================================
-- Explicação dos valores de status:
-- - 'ativa': Conversa em andamento (equivalente a 'open')
-- - 'pendente': Aguardando resposta (opcional)
-- - 'finalizada': Conversa concluída (equivalente a 'closed')
-- - 'cancelada': Conversa cancelada
-- - 'arquivada': Conversa arquivada (equivalente a 'archived')
-- ============================================================================

-- Pronto! A constraint foi corrigida.
-- Agora você pode inserir conversas com status: ativa, pendente, finalizada, cancelada, arquivada

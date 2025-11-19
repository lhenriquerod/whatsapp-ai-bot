-- Script para verificar e corrigir referências à tabela antiga "usuarios"

-- 1. Verificar todas as constraints que referenciam "usuarios"
SELECT
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE pg_get_constraintdef(oid) LIKE '%usuarios%';

-- 2. Remover constraint antiga se existir
ALTER TABLE conversations 
DROP CONSTRAINT IF EXISTS conversas_user_id_fkey;

ALTER TABLE conversations 
DROP CONSTRAINT IF EXISTS conversations_user_id_fkey;

-- 3. Criar nova constraint apontando para auth.users
ALTER TABLE conversations
ADD CONSTRAINT conversations_user_id_fkey 
FOREIGN KEY (user_id) 
REFERENCES auth.users(id) 
ON DELETE CASCADE;

-- 4. Verificar se há triggers que referenciam "usuarios"
SELECT 
    tgname AS trigger_name,
    tgrelid::regclass AS table_name,
    pg_get_triggerdef(oid) AS definition
FROM pg_trigger
WHERE pg_get_triggerdef(oid) LIKE '%usuarios%';

-- 5. Verificar views que referenciam "usuarios"
SELECT 
    schemaname,
    viewname,
    definition
FROM pg_views
WHERE definition LIKE '%usuarios%'
  AND schemaname = 'public';

-- 6. Se encontrar alguma view, recrie-a substituindo "usuarios" por "users"
-- (Execute manualmente conforme necessário)

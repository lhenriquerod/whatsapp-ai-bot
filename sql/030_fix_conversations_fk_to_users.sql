-- ===============================================
-- Migration 030: Fix conversations FK constraint
-- Change from 'usuarios' to 'users' table
-- ===============================================

-- 1. Drop the old constraint that references 'usuarios'
ALTER TABLE conversations
DROP CONSTRAINT IF EXISTS conversations_user_id_fkey;

-- 2. Add new constraint referencing 'users' table
ALTER TABLE conversations
ADD CONSTRAINT conversations_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 3. Same fix for messages table if it exists
ALTER TABLE messages
DROP CONSTRAINT IF EXISTS messages_user_id_fkey;

ALTER TABLE messages
ADD CONSTRAINT messages_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 4. Verify constraints
COMMENT ON CONSTRAINT conversations_user_id_fkey ON conversations IS 
  'FK to users table (migrated from usuarios)';

COMMENT ON CONSTRAINT messages_user_id_fkey ON messages IS 
  'FK to users table (migrated from usuarios)';

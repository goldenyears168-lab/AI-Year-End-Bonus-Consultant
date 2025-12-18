-- Supabase 對話記錄表結構（完整修復版本）
-- 請在 Supabase Dashboard > SQL Editor 中執行此 SQL
-- 
-- 重要：如果之前執行失敗，請先執行此 SQL 來清理並重建表

-- 步驟 1：刪除舊的策略（如果存在）
DROP POLICY IF EXISTS "Allow all operations for anon users" ON conversations;

-- 步驟 2：刪除舊的索引（如果存在）
DROP INDEX IF EXISTS idx_conversations_session_id;
DROP INDEX IF EXISTS idx_conversations_created_at;

-- 步驟 3：刪除舊的 conversations 表（如果存在）
DROP TABLE IF EXISTS conversations CASCADE;

-- 步驟 4：建立新的 conversations 表
CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 步驟 5：建立索引以加速查詢
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

-- 步驟 6：啟用 Row Level Security (RLS)
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- 步驟 7：建立策略：允許所有操作（因為我們使用 session_id 來區分會話）
CREATE POLICY "Allow all operations for anon users" 
    ON conversations 
    FOR ALL 
    USING (true) 
    WITH CHECK (true);

-- 驗證表結構
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'conversations'
ORDER BY ordinal_position;



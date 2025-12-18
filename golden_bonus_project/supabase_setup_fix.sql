-- Supabase 對話記錄表結構（修復版本）
-- 請在 Supabase Dashboard > SQL Editor 中執行此 SQL
-- 這個版本會先檢查並刪除舊表（如果存在），然後重新建立

-- 步驟 1：刪除舊的 conversations 表（如果存在）
DROP TABLE IF EXISTS conversations CASCADE;

-- 步驟 2：建立新的 conversations 表
CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 步驟 3：建立索引以加速查詢
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

-- 步驟 4：啟用 Row Level Security (RLS)
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- 步驟 5：建立策略：允許所有操作（因為我們使用 session_id 來區分會話）
-- 注意：這是一個簡化的策略，如果需要更嚴格的權限控制，可以根據需求調整
CREATE POLICY "Allow all operations for anon users" 
    ON conversations 
    FOR ALL 
    USING (true) 
    WITH CHECK (true);

-- 備註：
-- 1. session_id 對應 Streamlit 的 session_id，用來區分不同的對話會話
-- 2. role 只能是 'user' 或 'assistant'
-- 3. metadata 欄位可以存儲額外資訊（如 intent、company_context 等）
-- 4. created_at 自動記錄時間戳記


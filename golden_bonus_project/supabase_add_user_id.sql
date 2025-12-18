-- 可選：為 conversations 表添加 user_id 欄位（用於未來支持用戶登入）
-- 注意：這是可選的改進，如果當前不需要用戶登入功能，可以暫時不執行

-- 步驟 1：添加 user_id 欄位（允許 NULL，因為現有記錄沒有 user_id）
ALTER TABLE conversations 
ADD COLUMN IF NOT EXISTS user_id TEXT;

-- 步驟 2：為 user_id 建立索引（加速查詢）
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);

-- 步驟 3：建立複合索引（同時查詢 user_id 和 session_id）
CREATE INDEX IF NOT EXISTS idx_conversations_user_session ON conversations(user_id, session_id);

-- 步驟 4：添加註釋說明
COMMENT ON COLUMN conversations.user_id IS '用戶 ID（可選），如果有登入系統則填入，否則為 NULL，使用 session_id 區分會話';

-- 驗證：查看表結構
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'conversations'
ORDER BY ordinal_position;


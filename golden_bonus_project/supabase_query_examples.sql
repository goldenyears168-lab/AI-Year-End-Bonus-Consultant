-- Supabase 對話記錄查詢範例
-- 可以在 Supabase Dashboard > SQL Editor 中執行這些查詢

-- ============================================
-- 1. 查看所有不同的會話（每個會話的統計）
-- ============================================
SELECT 
    session_id,
    COUNT(*) as message_count,
    COUNT(CASE WHEN role = 'user' THEN 1 END) as user_messages,
    COUNT(CASE WHEN role = 'assistant' THEN 1 END) as assistant_messages,
    MIN(created_at) as first_message,
    MAX(created_at) as last_message,
    EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) / 60 as duration_minutes
FROM conversations
GROUP BY session_id
ORDER BY last_message DESC
LIMIT 20;

-- ============================================
-- 2. 查看特定會話的所有對話
-- ============================================
-- 替換 'your_session_id_here' 為實際的 session_id
SELECT 
    id,
    role,
    content,
    created_at,
    metadata
FROM conversations
WHERE session_id = 'demo_session_1766059426'  -- 替換為你的 session_id
ORDER BY created_at;

-- ============================================
-- 3. 查看最近的對話（所有用戶，最新 20 條）
-- ============================================
SELECT 
    id,
    session_id,
    role,
    LEFT(content, 100) as content_preview,  -- 只顯示前 100 個字符
    created_at
FROM conversations
ORDER BY created_at DESC
LIMIT 20;

-- ============================================
-- 4. 查看活躍會話（最近 24 小時內有活動的）
-- ============================================
SELECT 
    session_id,
    COUNT(*) as message_count,
    MAX(created_at) as last_activity,
    NOW() - MAX(created_at) as time_since_last_activity
FROM conversations
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY session_id
ORDER BY last_activity DESC;

-- ============================================
-- 5. 查看今天的對話統計
-- ============================================
SELECT 
    DATE(created_at) as date,
    COUNT(DISTINCT session_id) as unique_sessions,
    COUNT(*) as total_messages,
    COUNT(CASE WHEN role = 'user' THEN 1 END) as user_messages,
    COUNT(CASE WHEN role = 'assistant' THEN 1 END) as assistant_messages
FROM conversations
WHERE created_at >= CURRENT_DATE
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- ============================================
-- 6. 查看最活躍的會話（訊息數量最多）
-- ============================================
SELECT 
    session_id,
    COUNT(*) as total_messages,
    MIN(created_at) as started_at,
    MAX(created_at) as last_activity
FROM conversations
GROUP BY session_id
ORDER BY total_messages DESC
LIMIT 10;

-- ============================================
-- 7. 查看包含特定關鍵字的對話
-- ============================================
-- 例如：查找包含「稅務」的對話
SELECT 
    session_id,
    role,
    content,
    created_at
FROM conversations
WHERE content ILIKE '%稅務%'  -- ILIKE 是大小寫不敏感的搜尋
ORDER BY created_at DESC
LIMIT 20;

-- ============================================
-- 8. 查看特定時間範圍的對話
-- ============================================
SELECT 
    session_id,
    COUNT(*) as message_count,
    MIN(created_at) as first_message,
    MAX(created_at) as last_message
FROM conversations
WHERE created_at >= '2025-01-01'  -- 替換為你的開始日期
  AND created_at < '2025-01-02'   -- 替換為你的結束日期
GROUP BY session_id
ORDER BY first_message;

-- ============================================
-- 9. 查看每個會話的第一條和最後一條訊息
-- ============================================
WITH first_last AS (
    SELECT 
        session_id,
        FIRST_VALUE(content) OVER (PARTITION BY session_id ORDER BY created_at) as first_message,
        LAST_VALUE(content) OVER (PARTITION BY session_id ORDER BY created_at RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_message,
        MIN(created_at) OVER (PARTITION BY session_id) as first_time,
        MAX(created_at) OVER (PARTITION BY session_id) as last_time
    FROM conversations
)
SELECT DISTINCT
    session_id,
    LEFT(first_message, 80) as first_message_preview,
    LEFT(last_message, 80) as last_message_preview,
    first_time,
    last_time
FROM first_last
ORDER BY last_time DESC
LIMIT 20;

-- ============================================
-- 10. 統計總體數據
-- ============================================
SELECT 
    COUNT(*) as total_messages,
    COUNT(DISTINCT session_id) as total_sessions,
    COUNT(CASE WHEN role = 'user' THEN 1 END) as total_user_messages,
    COUNT(CASE WHEN role = 'assistant' THEN 1 END) as total_assistant_messages,
    MIN(created_at) as oldest_message,
    MAX(created_at) as newest_message
FROM conversations;


# 🔧 Supabase 對話記錄配置指南

## 📋 前置步驟

### 1. 在 Supabase 建立資料庫表

前往 [Supabase Dashboard](https://app.supabase.com) > 選擇你的專案 > SQL Editor，執行以下 SQL：

```sql
-- 檔案位置：supabase_setup.sql
-- 或直接複製以下 SQL 執行
```

完整 SQL 請參考 `supabase_setup.sql` 檔案，或執行：

```sql
CREATE TABLE IF NOT EXISTS conversations (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);

ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations for anon users" 
    ON conversations 
    FOR ALL 
    USING (true) 
    WITH CHECK (true);
```

### 2. 配置環境變數

#### 本地開發（使用 .env 檔案）

在 `golden_bonus_project/` 目錄下建立或編輯 `.env` 檔案：

```env
# Supabase 配置
NEXT_PUBLIC_SUPABASE_URL=https://gprjocjpibsqhdbncvga.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdwcmpvY2pwaWJzcWhkYm5jdmdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0Njc1NDAsImV4cCI6MjA4MDA0MzU0MH0.kuallDCX0DruwBxjfMhrdhm0jRgK3ODK75ppXJYOTRA
```

**⚠️ 重要**：`.env` 檔案已經在 `.gitignore` 中，不會被提交到 Git。

#### Streamlit Cloud（使用 Secrets）

1. 前往 [Streamlit Cloud](https://share.streamlit.io/)
2. 選擇你的應用
3. 點擊 "Settings" > "Secrets"
4. 新增以下 secrets：

```toml
SUPABASE_URL = "https://gprjocjpibsqhdbncvga.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdwcmpvY2pwaWJzcWhkYm5jdmdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0Njc1NDAsImV4cCI6MjA4MDA0MzU0MH0.kuallDCX0DruwBxjfMhrdhm0jRgK3ODK75ppXJYOTRA"
```

或者使用嵌套結構：

```toml
[supabase]
url = "https://gprjocjpibsqhdbncvga.supabase.co"
anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdwcmpvY2pwaWJzcWhkYm5jdmdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0Njc1NDAsImV4cCI6MjA4MDA0MzU0MH0.kuallDCX0DruwBxjfMhrdhm0jRgK3ODK75ppXJYOTRA"
```

### 3. 安裝依賴

```bash
cd golden_bonus_project
pip install -r requirements.txt
```

## 🧪 測試連線

### 方法 1：使用測試腳本

```bash
cd golden_bonus_project
python test_supabase.py
```

測試腳本會：
- ✅ 檢查環境變數配置
- ✅ 測試 Supabase 連線
- ✅ 測試對話保存和載入功能

### 方法 2：在 Streamlit 應用中測試

1. 啟動 Streamlit 應用：
   ```bash
   streamlit run main.py
   ```

2. 在側邊欄找到「💾 對話記錄」區塊
3. 點擊「測試 Supabase 連線」按鈕
4. 應該顯示「Supabase 連線成功，conversations 表可訪問」

## 📊 功能說明

### 對話記錄存儲

- **自動保存**：所有用戶訊息和 AI 回應會自動保存到 Supabase
- **自動載入**：頁面重新載入時，會自動從 Supabase 載入歷史對話（最多 50 條）
- **會話區分**：使用 Streamlit session_id 區分不同使用者的對話

### 資料結構

每條對話記錄包含：
- `session_id`: 會話識別碼（用來區分不同使用者的對話）
- `role`: 角色（"user" 或 "assistant"）
- `content`: 訊息內容
- `metadata`: 元數據（如 intent、company_context 等）
- `created_at`: 建立時間

## 🔍 查看對話記錄

前往 Supabase Dashboard > Table Editor > `conversations` 表，可以查看所有對話記錄。

可以按 `session_id` 篩選，查看特定使用者的對話歷史。

## ⚠️ 注意事項

1. **RLS 策略**：目前設定了允許所有操作的策略，如果需要在生產環境中更嚴格控制，請調整 RLS 策略
2. **資料清理**：長時間使用後，可能需要定期清理舊的對話記錄（可在 Supabase 中設定自動清理規則）
3. **性能考量**：載入歷史對話時限制為 50 條，避免載入過多資料影響性能

## 🐛 故障排除

### 問題 1：連線測試失敗，顯示「表不存在」

**解決方案**：執行 `supabase_setup.sql` 中的 SQL 建立表結構

### 問題 2：連線測試失敗，顯示「未找到 SUPABASE_URL」

**解決方案**：
- 本地：檢查 `.env` 檔案是否存在且包含正確的環境變數
- Streamlit Cloud：檢查 Secrets 是否正確設定

### 問題 3：保存對話失敗但沒有錯誤訊息

**解決方案**：
- 檢查 Supabase 表的 RLS 策略是否正確設定
- 檢查 API Key 權限是否足夠（應該使用 anon key）

## 📝 相關檔案

- `utils/conversation_storage.py`: Supabase 連線和對話存儲模組
- `supabase_setup.sql`: 資料庫表結構 SQL
- `test_supabase.py`: 測試腳本
- `main.py`: 主應用程式（已整合對話記錄功能）


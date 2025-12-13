# 🚀 Streamlit Cloud 部署指南

## 🔍 問題診斷

從您的截圖看到，Streamlit Cloud 部署表單有以下錯誤：
1. Repository 欄位顯示錯誤的 repo 名稱
2. Branch 顯示 "master" 但應該是 "main"
3. Main file path 顯示 "streamlit_app.py" 但應該是 "golden_bonus_project/main.py"

## ✅ 正確的部署設定

### 1. Repository（倉庫名稱）

**正確值**：
```
goldenyears168-lab/AI-Year-End-Bonus-Consultant
```

**如何填寫**：
- 點擊 "Paste GitHub URL" 連結
- 或直接輸入：`goldenyears168-lab/AI-Year-End-Bonus-Consultant`

### 2. Branch（分支名稱）

**正確值**：
```
main
```

**注意**：不是 "master"，是 "main"

### 3. Main file path（主檔案路徑）

**正確值**：
```
golden_bonus_project/main.py
```

**說明**：因為 `main.py` 在 `golden_bonus_project/` 子目錄中

## 📝 完整部署步驟

### 步驟 1：前往 Streamlit Cloud

1. 前往 [Streamlit Cloud](https://streamlit.io/cloud)
2. 登入您的帳號（使用 GitHub 帳號登入）
3. 點擊 "New app"

### 步驟 2：填寫部署表單

按照以下設定填寫：

| 欄位 | 值 |
|------|-----|
| **Repository** | `goldenyears168-lab/AI-Year-End-Bonus-Consultant` |
| **Branch** | `main` |
| **Main file path** | `golden_bonus_project/main.py` |
| **App URL** | （可選，留空或自訂） |

### 步驟 3：設定 Secrets（API Key）

在 "Advanced settings" 中設定 Secrets：

1. 點擊 "Advanced settings"
2. 找到 "Secrets" 區塊
3. 點擊 "New secret"
4. 新增：
   - **Key**: `GEMINI_API_KEY`
   - **Value**: `AIzaSyD8YF-WMvUdDJOIJ8p7Eh9B06-I_ZfPJVs`

### 步驟 4：部署

點擊 "Deploy" 按鈕，等待部署完成。

## ⚠️ 常見問題

### 問題 1：找不到 Repository

**解決方案**：
1. 確認已授權 Streamlit Cloud 存取您的 GitHub 帳號
2. 確認 Repository 是 Public 或您有權限存取
3. 嘗試重新整理頁面

### 問題 2：Branch 不存在

**解決方案**：
- 確認分支名稱是 `main` 不是 `master`
- 在 GitHub 上確認分支確實存在

### 問題 3：Main file path 錯誤

**解決方案**：
- 確認路徑是 `golden_bonus_project/main.py`
- 在 GitHub 上確認檔案路徑正確

### 問題 4：部署後 API Key 錯誤

**解決方案**：
- 確認已在 Streamlit Cloud Secrets 中設定 `GEMINI_API_KEY`
- 確認 Key 名稱完全一致（大小寫敏感）

## 🔧 如果 Repository 還是找不到

### 方法 1：使用 GitHub URL

在 Repository 欄位中，點擊 "Paste GitHub URL"，然後貼上：
```
https://github.com/goldenyears168-lab/AI-Year-End-Bonus-Consultant
```

### 方法 2：重新授權

1. 前往 Streamlit Cloud Settings
2. 取消授權 GitHub
3. 重新授權並選擇正確的組織/帳號

### 方法 3：確認 Repository 可見性

1. 前往 GitHub Repository 設定
2. 確認 Repository 是 Public 或您已授權 Streamlit Cloud 存取

## 📋 部署檢查清單

在部署前，確認：

- [ ] Repository 名稱正確：`goldenyears168-lab/AI-Year-End-Bonus-Consultant`
- [ ] Branch 名稱正確：`main`
- [ ] Main file path 正確：`golden_bonus_project/main.py`
- [ ] 已在 Streamlit Cloud Secrets 中設定 `GEMINI_API_KEY`
- [ ] `.env` 檔案**沒有**被推送到 GitHub（這是正確的）
- [ ] `venv/` 目錄**沒有**被推送到 GitHub（這是正確的）

## 🎯 快速參考

**正確的部署設定**：
```
Repository: goldenyears168-lab/AI-Year-End-Bonus-Consultant
Branch: main
Main file path: golden_bonus_project/main.py
Secrets: GEMINI_API_KEY = AIzaSyD8YF-WMvUdDJOIJ8p7Eh9B06-I_ZfPJVs
```

## 🆘 如果還是有問題

1. **檢查 GitHub Repository**：
   - 前往 https://github.com/goldenyears168-lab/AI-Year-End-Bonus-Consultant
   - 確認 `golden_bonus_project/main.py` 檔案存在
   - 確認分支是 `main`

2. **檢查 Streamlit Cloud 權限**：
   - 確認已授權存取該 Repository
   - 確認 Repository 可見性設定正確

3. **查看部署日誌**：
   - 在 Streamlit Cloud 中查看部署日誌
   - 檢查是否有錯誤訊息

---

**現在請使用正確的設定重新部署！**


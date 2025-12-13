# 📤 GitHub 同步指南

## 🔍 當前狀態

目前專案**只在本地**，尚未同步到 GitHub。

## 🚀 推送到 GitHub 的步驟

### 步驟 1：初始化 Git（如果還沒初始化）

```bash
# 確認您在專案目錄中
cd golden_bonus_project

# 初始化 Git 倉庫
git init
```

### 步驟 2：設定 Git 用戶資訊（如果還沒設定）

```bash
# 設定您的名稱和郵箱（只需要執行一次）
git config --global user.name "您的名稱"
git config --global user.email "您的郵箱"
```

### 步驟 3：加入所有檔案到 Git

```bash
# 加入所有檔案（.gitignore 會自動排除 .env 和 venv）
git add .

# 查看將要提交的檔案（確認 .env 不會被加入）
git status
```

### 步驟 4：建立第一次提交

```bash
git commit -m "Initial commit: GoldenBonus AI 年終獎金顧問系統"
```

### 步驟 5：在 GitHub 建立新倉庫

1. 前往 [GitHub](https://github.com)
2. 點擊右上角的 **+** → **New repository**
3. 填寫倉庫資訊：
   - Repository name: `golden-bonus-ai`（或您喜歡的名稱）
   - Description: `AI 年終獎金分配顧問系統`
   - 選擇 **Public** 或 **Private**
   - **不要**勾選 "Initialize this repository with a README"（因為我們已經有檔案了）
4. 點擊 **Create repository**

### 步驟 6：連接本地倉庫到 GitHub

```bash
# 複製 GitHub 提供的倉庫 URL（例如：https://github.com/您的用戶名/golden-bonus-ai.git）
# 然後執行：

git remote add origin https://github.com/您的用戶名/golden-bonus-ai.git

# 確認遠端倉庫已連接
git remote -v
```

### 步驟 7：推送到 GitHub

```bash
# 推送到 GitHub（第一次推送）
git branch -M main
git push -u origin main
```

## ✅ 驗證同步成功

1. 前往您的 GitHub 倉庫頁面
2. 確認所有檔案都已上傳
3. 確認 `.env` 檔案**沒有**出現在 GitHub 上（這是正確的，因為它在 .gitignore 中）

## 🔄 後續更新流程

當您修改程式碼後，使用以下命令更新 GitHub：

```bash
# 1. 查看變更
git status

# 2. 加入變更的檔案
git add .

# 3. 提交變更
git commit -m "描述您的變更"

# 4. 推送到 GitHub
git push
```

## ⚠️ 重要提醒

### 絕對不要上傳的檔案

以下檔案已在 `.gitignore` 中，不會被上傳：
- `.env` - 包含您的 API Key（機密）
- `venv/` - 虛擬環境（太大且不需要）
- `__pycache__/` - Python 快取檔案

### 確認 .env 不會被上傳

在推送前，執行以下命令確認：

```bash
git status
```

如果看到 `.env` 在列表中，執行：

```bash
git rm --cached .env
git commit -m "Remove .env from tracking"
```

## 📝 快速指令參考

```bash
# 初始化並推送（完整流程）
git init
git add .
git commit -m "Initial commit: GoldenBonus AI"
git remote add origin https://github.com/您的用戶名/golden-bonus-ai.git
git branch -M main
git push -u origin main
```

## 🆘 常見問題

### 問題：推送時要求輸入帳號密碼

**解決方案**：使用 Personal Access Token（PAT）
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 建立新 token，勾選 `repo` 權限
3. 推送時使用 token 作為密碼

### 問題：.env 檔案被上傳了

**解決方案**：
```bash
# 從 Git 中移除（但保留本地檔案）
git rm --cached .env
git commit -m "Remove .env"
git push
```

### 問題：venv 目錄被上傳了

**解決方案**：
```bash
# 從 Git 中移除
git rm -r --cached venv
git commit -m "Remove venv"
git push
```

## 🎯 下一步

完成推送後，您可以：
1. 在 GitHub 上查看程式碼
2. 與團隊分享專案
3. 使用 GitHub Actions 進行 CI/CD（可選）
4. 部署到 Streamlit Cloud（可選）

---

**提示**：如果這是您的第一個 GitHub 專案，建議先閱讀 [GitHub 入門指南](https://docs.github.com/en/get-started)


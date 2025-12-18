# 🔍 本地成功但 Streamlit Cloud 失敗的常見原因

## 已確認：本地測試成功 ✅

既然本地可以成功啟動，說明代碼本身沒有問題。問題出在 Streamlit Cloud 的環境或配置上。

## 可能的原因和解決方案

### 原因 1：文件沒有提交到 GitHub ⚠️ 最常見

**檢查方法：**
```bash
cd golden_bonus_project
git status
```

**如果看到 `assets/__init__.py` 或 `main.py` 顯示為 "Untracked files" 或 "Changes not staged"：**

```bash
# 添加並提交文件
git add assets/__init__.py
git add main.py  # 如果有修改
git commit -m "Fix: Add assets __init__.py and fix import paths"
git push
```

### 原因 2：Streamlit Cloud 的 Main file path 設定錯誤

**檢查 Streamlit Cloud 設置：**

Main file path 應該是：
```
golden_bonus_project/main.py
```

**不是：**
- ❌ `main.py`（缺少目錄前綴）
- ❌ `golden_bonus_project/main.py/`（結尾不要斜線）
- ❌ `./golden_bonus_project/main.py`（不要相對路徑）

### 原因 3：依賴版本不兼容

Streamlit Cloud 可能使用不同版本的 Python 或依賴。

**檢查 `requirements.txt`：**
```txt
streamlit>=1.30.0
google-generativeai>=0.3.0
python-dotenv>=1.0.0
supabase>=2.0.0
```

確保版本要求不要太嚴格，使用 `>=` 而不是 `==`。

### 原因 4：Secrets 配置缺失或錯誤

Streamlit Cloud 需要 Secrets 來配置環境變數。

**檢查 Streamlit Cloud > Settings > Secrets：**

```toml
GEMINI_API_KEY = "你的 Gemini API Key"
SUPABASE_URL = "https://gprjocjpibsqhdbncvga.supabase.co"
SUPABASE_ANON_KEY = "你的 Supabase Anon Key"
```

### 原因 5：Python 版本差異

本地和 Cloud 的 Python 版本可能不同。

**檢查：**
- Streamlit Cloud 默認使用 Python 3.9
- 如果本地使用 Python 3.10+，可能有兼容性問題

可以在 `requirements.txt` 中指定 Python 版本（但 Streamlit Cloud 可能不支持）。

### 原因 6：文件路徑問題（已修復但需確認）

我們已經在 `main.py` 中添加了路徑處理，但需要確認：

1. 這段代碼是否已提交：
```python
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
```

2. `assets/__init__.py` 是否已提交

## 🚀 立即執行的檢查步驟

### 步驟 1：確認文件已提交

```bash
cd golden_bonus_project
git status
```

如果有未提交的文件，執行：
```bash
git add .
git commit -m "Fix: Add missing files for Streamlit Cloud deployment"
git push
```

### 步驟 2：確認 Streamlit Cloud 設置

在 Streamlit Cloud Dashboard：
1. 檢查 Main file path: `golden_bonus_project/main.py`
2. 檢查 Branch: `main`
3. 檢查 Secrets 是否已配置

### 步驟 3：查看 Streamlit Cloud 的完整錯誤日誌

1. 點擊應用名稱
2. 找到 "Logs" 或點擊最新部署
3. 查看完整的錯誤訊息
4. 複製 `Traceback` 部分的錯誤

## 💡 診斷技巧

### 對比本地和 Cloud 的差異

本地成功 → 檢查：
- ✅ 代碼沒有問題
- ✅ 依賴安裝成功
- ✅ 環境變數配置正確

Cloud 失敗 → 檢查：
- ⚠️ 文件是否都在 GitHub
- ⚠️ Main file path 是否正確
- ⚠️ Secrets 是否配置
- ⚠️ Python 版本是否兼容

## 🎯 最可能的原因

根據經驗，90% 的情況是：
1. **文件沒有提交到 GitHub**（特別是 `assets/__init__.py`）
2. **Main file path 設定錯誤**

請先確認這兩個項目！


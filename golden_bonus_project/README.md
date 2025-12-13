# 🤖 GoldenBonus AI - 年終獎金顧問系統

一個基於 Streamlit 和 Gemini API 的智能年終獎金分配顧問系統，採用麥肯錫級別的顧問思維，協助 CEO 制定年終獎金策略。

## 📋 專案簡介

GoldenBonus AI 是一個決策引擎，而非簡單的計算器。它將企業主的財務數據轉化為戰略建議，採用「黃金三段式」輸出格式，提供：
- 🎯 戰略判斷 (The Verdict)
- ⚖️ 取捨分析 (The Trade-off)
- 💬 關鍵對話 (The Script)

## 🚀 快速開始

### 1. 環境設置

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定 API Key
cp .env.example .env
# 編輯 .env 檔案，填入你的 GEMINI_API_KEY
```

### 2. 執行應用

```bash
streamlit run main.py
```

### 3. 使用流程

1. 在側邊欄填寫企業數據（營收、淨利、員工數等）
2. 調整「CEO 決策槓桿」（生存槓桿、激勵槓桿、現實槓桿）
3. 點擊「🚀 開始分析 / 生成草案」
4. 查看 AI 生成的決策備忘錄
5. 使用互動諮詢區進行進一步問答

## 📁 專案結構

```
golden_bonus_project/
├── main.py                 # 主程式入口
├── requirements.txt       # 依賴清單
├── .env.example           # 環境變數範例
├── .gitignore            # Git 忽略檔案
│
├── core/                  # 核心引擎
│   ├── base_node.py      # 節點基類
│   └── pipeline.py       # Pipeline 執行器
│
├── nodes/                 # 業務邏輯節點
│   ├── calculator.py     # 計算節點（含風險檢查）
│   └── advisor.py        # AI 顧問節點
│
├── assets/                # 靜態資源
│   └── knowledge.py      # 知識庫（集中編輯區）
│
├── config/                # 配置中心
│   └── settings.py       # 表單欄位、提示詞、快捷問題（集中編輯區）
│
└── utils/                 # 工具函數
    └── gemini_client.py  # Gemini API 客戶端
```

## ⚙️ 配置說明

### 修改知識庫內容

編輯 `assets/knowledge.py` 中的 `BONUS_KB_TEXT` 變數。

### 修改表單欄位

編輯 `config/settings.py` 中的 `FORM_FIELDS` 字典。

### 修改快捷問題

編輯 `config/settings.py` 中的 `QUICK_QUESTIONS` 字典。

### 修改提示詞模板

編輯 `config/settings.py` 中的 `PROMPT_TEMPLATES` 字典。

## 🔧 技術架構

- **前端**：Streamlit
- **AI 模型**：Google Gemini 2.0 Flash (gemini-2.0-flash-exp)
- **架構模式**：Pipeline + Node（可擴展的模組化設計）
- **狀態管理**：Streamlit Session State

## 📝 開發指南

詳細的開發步驟請參考 `開發步驟指南.md`。

## ⚠️ 注意事項

1. **API Key 安全**：絕對不要將 `.env` 檔案上傳到 GitHub
2. **數據同步**：調整 Sidebar 數據後，必須重新生成報告才能開始聊天
3. **單位換算**：注意 `net_profit` 是萬元，`avg_salary` 是元

## 📄 授權

本專案僅供學習和內部使用。

## 🆘 問題排除

### ImportError: No module named 'core'

確認當前目錄是專案根目錄，且所有 `__init__.py` 檔案都存在。

### API Key 錯誤

檢查 `.env` 檔案中的 `GEMINI_API_KEY` 是否正確設定。

### 狀態重置問題

確認所有需要持久化的數據都存到 `st.session_state`，且 `reset_on_change` 回調函數正確設定。

---

**版本**：v1.0  
**最後更新**：2024-12-13


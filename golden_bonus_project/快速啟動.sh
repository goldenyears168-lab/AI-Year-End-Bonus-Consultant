#!/bin/bash
# 快速啟動腳本

echo "🚀 啟動 GoldenBonus AI..."
echo ""

# 檢查 .env 檔案
if [ ! -f .env ]; then
    echo "⚠️  警告：未找到 .env 檔案"
    echo "   請建立 .env 檔案並填入 GEMINI_API_KEY"
    exit 1
fi

# 檢查依賴
echo "📦 檢查依賴套件..."
python3 -c "import streamlit" 2>/dev/null || {
    echo "❌ Streamlit 未安裝，正在安裝..."
    pip3 install -q streamlit google-generativeai python-dotenv
}

# 啟動應用
echo "✅ 啟動 Streamlit 應用..."
echo ""
streamlit run main.py


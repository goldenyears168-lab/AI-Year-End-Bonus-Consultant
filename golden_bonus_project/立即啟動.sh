#!/bin/bash
# 立即啟動 GoldenBonus AI

echo "🚀 啟動 GoldenBonus AI..."
echo ""

# 確認當前目錄
if [ ! -f "main.py" ]; then
    echo "❌ 錯誤：找不到 main.py"
    echo "   請確認您在 golden_bonus_project 目錄中"
    exit 1
fi

# 檢查依賴
echo "📦 檢查依賴..."
python3 -c "import streamlit" 2>/dev/null || {
    echo "⚠️  Streamlit 未安裝，正在安裝..."
    python3 -m pip install --user streamlit google-generativeai python-dotenv
}

# 啟動應用
echo ""
echo "✅ 啟動 Streamlit 應用..."
echo "   瀏覽器會自動打開 http://localhost:8501"
echo ""
python3 -m streamlit run main.py


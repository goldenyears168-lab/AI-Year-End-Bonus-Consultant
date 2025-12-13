#!/bin/bash
# 啟動 GoldenBonus AI（使用虛擬環境）

cd "$(dirname "$0")"

# 檢查虛擬環境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 虛擬環境不存在，正在建立..."
    python3 -m venv venv
    echo "📦 安裝依賴..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "✅ 啟動虛擬環境..."
    source venv/bin/activate
fi

echo ""
echo "🚀 啟動 Streamlit 應用..."
echo "   瀏覽器會自動打開 http://localhost:8501"
echo ""

streamlit run main.py


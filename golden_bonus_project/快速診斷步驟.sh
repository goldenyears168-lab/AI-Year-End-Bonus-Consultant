#!/bin/bash
# 快速診斷腳本 - 檢查所有可能的問題

echo "========================================="
echo "Streamlit Cloud 部署問題快速診斷"
echo "========================================="
echo ""

# 1. 檢查關鍵文件是否存在
echo "1. 檢查關鍵文件..."
files=(
    "main.py"
    "requirements.txt"
    "assets/__init__.py"
    "assets/knowledge.py"
    "assets/1-company_info.json"
    "assets/2-ai_config.json"
    "assets/3-knowledge_base.json"
    "config/__init__.py"
    "config/settings.py"
    "core/__init__.py"
    "core/base_node.py"
    "core/pipeline.py"
    "nodes/__init__.py"
    "nodes/advisor.py"
    "utils/__init__.py"
    "utils/gemini_client.py"
    "utils/conversation_storage.py"
)

missing_files=()
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (缺失)"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  發現缺失文件："
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
else
    echo ""
    echo "✅ 所有關鍵文件都存在"
fi

echo ""

# 2. 檢查 Python 語法
echo "2. 檢查 Python 語法..."
python3 -m py_compile main.py 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ main.py 語法正確"
else
    echo "  ❌ main.py 有語法錯誤"
fi

echo ""

# 3. 檢查導入
echo "3. 測試導入..."
python3 diagnose_imports.py 2>&1 | grep -E "(✅|❌|Traceback)" | head -20

echo ""
echo "========================================="
echo "診斷完成"
echo "========================================="
echo ""
echo "下一步："
echo "1. 如果發現缺失文件，請確認已提交到 GitHub"
echo "2. 如果有語法錯誤，請修復"
echo "3. 如果有導入錯誤，請查看完整輸出"
echo "4. 將診斷結果發給 AI 助手進行分析"


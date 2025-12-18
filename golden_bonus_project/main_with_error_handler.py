# main_with_error_handler.py
# 這是一個帶有詳細錯誤處理的版本，用於診斷問題
import sys
import os
from pathlib import Path

# 確保可以導入同目錄下的模組（解決 Streamlit Cloud 部署時的導入問題）
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# 在導入 Streamlit 之前，先嘗試導入所有模組並捕獲錯誤
print("=" * 70, file=sys.stderr)
print("開始診斷導入...", file=sys.stderr)
print(f"工作目錄: {current_dir}", file=sys.stderr)
print(f"Python 路徑前3個: {sys.path[:3]}", file=sys.stderr)
print("=" * 70, file=sys.stderr)

# 測試導入並輸出詳細信息
try:
    import streamlit as st
    print("✅ streamlit 導入成功", file=sys.stderr)
except Exception as e:
    print(f"❌ streamlit 導入失敗: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)

try:
    from nodes.advisor import AdvisorNode
    print("✅ nodes.advisor 導入成功", file=sys.stderr)
except Exception as e:
    print(f"❌ nodes.advisor 導入失敗: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)

try:
    from core.pipeline import Pipeline
    print("✅ core.pipeline 導入成功", file=sys.stderr)
except Exception as e:
    print(f"❌ core.pipeline 導入失敗: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)

try:
    from config.settings import PAGE_TITLE, PAGE_HEADER, PIPELINE_CACHE_VERSION
    print(f"✅ config.settings 導入成功: {PAGE_TITLE}", file=sys.stderr)
except Exception as e:
    print(f"❌ config.settings 導入失敗: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)

print("=" * 70, file=sys.stderr)
print("導入診斷完成，繼續執行主程序...", file=sys.stderr)
print("=" * 70, file=sys.stderr)

# 現在導入主程序（從原始的 main.py）
import streamlit as st
from nodes.advisor import AdvisorNode
from core.pipeline import Pipeline
from config.settings import PAGE_TITLE, PAGE_HEADER, PIPELINE_CACHE_VERSION

def looks_like_company_report_payload(text: str) -> bool:
    """
    判斷使用者是否貼上「結構化公司補充資訊」。
    嚴格但不依賴 report: 開頭：只要包含 company: 且同時包含其他常見區塊即可。
    """
    t = (text or "").lower()
    if "company" not in t:
        return False
    blocks = ["financials", "bonus", "departments", "growthengine", "warnings", "recommendations"]
    return any(b in t for b in blocks)

# 1. 頁面設定
st.set_page_config(page_title=PAGE_TITLE, layout="wide")
st.title(PAGE_HEADER)

# 顯示診斷信息
with st.expander("🔍 診斷信息（展開查看）", expanded=False):
    st.code(f"""
工作目錄: {current_dir}
Python 版本: {sys.version}
已載入模組:
- streamlit: ✅
- nodes.advisor: ✅
- core.pipeline: ✅
- config.settings: ✅
    """)

# 其餘代碼從 main.py 複製...（這裡只是示例，實際使用時需要複製完整的 main.py 內容）


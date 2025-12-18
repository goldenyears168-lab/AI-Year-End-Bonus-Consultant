#!/usr/bin/env python3
"""
詳細的導入診斷腳本
用於檢查所有模組是否可以正確導入
"""
import sys
from pathlib import Path

# 添加當前目錄到路徑（模擬 main.py 的做法）
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

print("=" * 70)
print("導入診斷開始")
print("=" * 70)
print(f"工作目錄: {current_dir}")
print(f"Python 路徑: {sys.path[:3]}")
print()

# 測試基礎模組
print("1. 測試基礎 Python 模組...")
try:
    import os
    print("   ✅ os")
except Exception as e:
    print(f"   ❌ os: {e}")
    sys.exit(1)

try:
    from pathlib import Path
    print("   ✅ pathlib")
except Exception as e:
    print(f"   ❌ pathlib: {e}")
    sys.exit(1)

# 測試第三方依賴
print("\n2. 測試第三方依賴...")
deps = [
    ("streamlit", "st"),
    ("google.generativeai", "genai"),
    ("dotenv", "dotenv"),
    ("supabase", "supabase"),
]

for module_name, alias in deps:
    try:
        module = __import__(module_name)
        print(f"   ✅ {module_name}")
    except ImportError as e:
        print(f"   ❌ {module_name}: {e}")
    except Exception as e:
        print(f"   ⚠️  {module_name}: {e} (非 ImportError)")

# 測試項目模組
print("\n3. 測試項目模組（按依賴順序）...")

# 3.1 基礎模組（無依賴）
modules = [
    ("core.base_node", "BaseNode"),
    ("core.pipeline", "Pipeline"),
    ("config.settings", ["PAGE_TITLE", "PAGE_HEADER", "PIPELINE_CACHE_VERSION"]),
]

for module_path, items in modules:
    try:
        module = __import__(module_path, fromlist=items if isinstance(items, list) else [])
        print(f"   ✅ {module_path}")
        if isinstance(items, list):
            for item in items:
                if hasattr(module, item):
                    print(f"      ✅ {item}")
                else:
                    print(f"      ❌ {item} 不存在")
        elif hasattr(module, items):
            print(f"      ✅ {items}")
        else:
            print(f"      ❌ {items} 不存在")
    except Exception as e:
        print(f"   ❌ {module_path}: {e}")
        import traceback
        traceback.print_exc()

# 3.2 測試 assets.knowledge（可能有文件讀取）
print("\n4. 測試 assets.knowledge...")
try:
    from assets.knowledge import BONUS_KB_TEXT
    print(f"   ✅ assets.knowledge")
    print(f"      BONUS_KB_TEXT 類型: {type(BONUS_KB_TEXT)}")
    print(f"      BONUS_KB_TEXT 長度: {len(BONUS_KB_TEXT) if isinstance(BONUS_KB_TEXT, str) else 'N/A'}")
except Exception as e:
    print(f"   ❌ assets.knowledge: {e}")
    import traceback
    traceback.print_exc()

# 3.3 測試 nodes.advisor
print("\n5. 測試 nodes.advisor...")
try:
    from nodes.advisor import AdvisorNode
    print(f"   ✅ nodes.advisor")
    print(f"      AdvisorNode: {AdvisorNode}")
except Exception as e:
    print(f"   ❌ nodes.advisor: {e}")
    import traceback
    traceback.print_exc()

# 3.4 測試 utils 模組
print("\n6. 測試 utils 模組...")
utils_modules = [
    ("utils.gemini_client", ["get_api_key", "test_gemini_connection"]),
    ("utils.conversation_storage", ["get_supabase_config", "test_supabase_connection"]),
]

for module_path, functions in utils_modules:
    try:
        module = __import__(module_path, fromlist=functions)
        print(f"   ✅ {module_path}")
        for func in functions:
            if hasattr(module, func):
                print(f"      ✅ {func}")
            else:
                print(f"      ❌ {func} 不存在")
    except Exception as e:
        print(f"   ❌ {module_path}: {e}")
        import traceback
        traceback.print_exc()

# 7. 嘗試完整導入 main.py 的導入部分
print("\n7. 測試 main.py 的導入順序...")
try:
    import streamlit as st
    print("   ✅ import streamlit as st")
except Exception as e:
    print(f"   ❌ import streamlit as st: {e}")
    sys.exit(1)

try:
    from nodes.advisor import AdvisorNode
    print("   ✅ from nodes.advisor import AdvisorNode")
except Exception as e:
    print(f"   ❌ from nodes.advisor import AdvisorNode: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from core.pipeline import Pipeline
    print("   ✅ from core.pipeline import Pipeline")
except Exception as e:
    print(f"   ❌ from core.pipeline import Pipeline: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from config.settings import PAGE_TITLE, PAGE_HEADER, PIPELINE_CACHE_VERSION
    print("   ✅ from config.settings import PAGE_TITLE, PAGE_HEADER, PIPELINE_CACHE_VERSION")
    print(f"      PAGE_TITLE = {PAGE_TITLE}")
except Exception as e:
    print(f"   ❌ from config.settings import ...: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ 所有導入測試通過！")
print("=" * 70)


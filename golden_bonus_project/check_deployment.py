#!/usr/bin/env python3
"""
部署前檢查腳本
檢查所有必要的模組和配置是否正確
"""
import sys

def check_imports():
    """檢查所有必要的導入"""
    print("=" * 60)
    print("檢查模組導入...")
    print("=" * 60)
    
    modules = [
        ("streamlit", "Streamlit"),
        ("google.generativeai", "Google Generative AI"),
        ("dotenv", "python-dotenv"),
        ("supabase", "Supabase"),
    ]
    
    failed = []
    for module, name in modules:
        try:
            __import__(module)
            print(f"✅ {name} 導入成功")
        except ImportError as e:
            print(f"❌ {name} 導入失敗: {str(e)}")
            failed.append(name)
    
    return len(failed) == 0


def check_config():
    """檢查配置"""
    print("\n" + "=" * 60)
    print("檢查配置...")
    print("=" * 60)
    
    # 檢查環境變數（本地）
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    configs = [
        ("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY")),
        ("SUPABASE_URL", os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")),
        ("SUPABASE_ANON_KEY", os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")),
    ]
    
    missing = []
    for name, value in configs:
        if value:
            print(f"✅ {name} 已配置")
        else:
            print(f"⚠️  {name} 未配置（在 Streamlit Cloud 中應該在 Secrets 中）")
            if "SUPABASE" not in name:  # Supabase 是可選的
                missing.append(name)
    
    return len(missing) == 0


def check_project_structure():
    """檢查專案結構"""
    print("\n" + "=" * 60)
    print("檢查專案結構...")
    print("=" * 60)
    
    import os
    
    required_files = [
        "main.py",
        "requirements.txt",
        "utils/conversation_storage.py",
        "utils/gemini_client.py",
        "config/settings.py",
        "nodes/advisor.py",
        "core/pipeline.py",
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} 不存在")
            all_exist = False
    
    return all_exist


def check_supabase_connection():
    """測試 Supabase 連線（可選）"""
    print("\n" + "=" * 60)
    print("測試 Supabase 連線（可選）...")
    print("=" * 60)
    
    try:
        from utils.conversation_storage import test_supabase_connection
        ok, msg = test_supabase_connection()
        if ok:
            print(f"✅ {msg}")
            return True
        else:
            print(f"⚠️  {msg}（這不影響應用啟動）")
            return True  # Supabase 是可選的
    except Exception as e:
        print(f"⚠️  Supabase 測試失敗: {str(e)}（這不影響應用啟動）")
        return True  # Supabase 是可選的


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Streamlit 應用部署前檢查")
    print("=" * 60 + "\n")
    
    results = []
    
    # 檢查導入
    results.append(("模組導入", check_imports()))
    
    # 檢查配置
    results.append(("配置檢查", check_config()))
    
    # 檢查專案結構
    results.append(("專案結構", check_project_structure()))
    
    # 檢查 Supabase（可選）
    check_supabase_connection()
    
    # 總結
    print("\n" + "=" * 60)
    print("檢查結果總結")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有必要檢查通過！可以部署")
        return 0
    else:
        print("❌ 部分檢查失敗，請修復後再部署")
        return 1


if __name__ == "__main__":
    sys.exit(main())


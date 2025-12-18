# utils/conversation_storage.py
"""
對話記錄存儲模組：使用 Supabase 持久化對話歷史
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
try:
    import streamlit as st  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    st = None  # 允許在非 Streamlit 環境下 import

# 自動判斷是本地開發還是雲端
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ModuleNotFoundError:
    pass


def get_supabase_config() -> tuple[Optional[str], Optional[str]]:
    """
    獲取 Supabase 配置，優先使用 Streamlit Secrets（雲端），其次使用環境變數（本地）
    
    Returns:
        tuple: (supabase_url, supabase_key) 或 (None, None) 如果未配置
    """
    url = None
    key = None
    
    # 優先使用 Streamlit Secrets（適用於 Streamlit Cloud）
    try:
        if st is not None and hasattr(st, 'secrets') and st.secrets:
            secrets = st.secrets
            # 嘗試從 secrets 中讀取（可以是嵌套結構）
            if hasattr(secrets, 'get'):
                url = secrets.get("SUPABASE_URL") or secrets.get("supabase", {}).get("url")
                key = secrets.get("SUPABASE_ANON_KEY") or secrets.get("supabase", {}).get("anon_key")
    except Exception:
        pass
    
    # 其次使用環境變數（適用於本地開發）
    if not url:
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    if not key:
        key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    return (url, key)


def get_supabase_client():
    """
    獲取 Supabase 客戶端實例
    
    Returns:
        supabase.Client 或 None（如果配置缺失）
    """
    try:
        from supabase import create_client, Client
    except ImportError:
        return None
    
    url, key = get_supabase_config()
    if not url or not key:
        return None
    
    try:
        client: Client = create_client(url, key)
        return client
    except Exception:
        return None


def save_conversation(session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    保存單條對話訊息到 Supabase
    
    Args:
        session_id: Streamlit session ID（用於區分不同會話）
        role: 角色（"user" 或 "assistant"）
        content: 訊息內容
        metadata: 可選的元數據（如 intent、company_context 等）
    
    Returns:
        bool: 是否成功保存
    """
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        data = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        # 注意：created_at 會由資料庫自動設定，不需要手動傳入
        
        result = client.table("conversations").insert(data).execute()
        return len(result.data) > 0
    except Exception as e:
        # 在測試模式下輸出錯誤信息，幫助調試
        import sys
        if "test" in sys.argv[0].lower() or "test_supabase" in sys.argv[0]:
            print(f"    錯誤詳情: {str(e)}")
        # 靜默失敗，不影響主流程
        return False


def load_conversation_history(session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    從 Supabase 載入指定會話的對話歷史
    
    Args:
        session_id: Streamlit session ID
        limit: 最多載入的訊息數量
    
    Returns:
        List[Dict]: 對話訊息列表，格式為 [{"role": "user/assistant", "content": "..."}]
    """
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        result = (
            client.table("conversations")
            .select("role, content")
            .eq("session_id", session_id)
            .order("created_at")
            .limit(limit)
            .execute()
        )
        
        # 轉換為標準格式
        messages = []
        for row in result.data:
            messages.append({
                "role": row.get("role", ""),
                "content": row.get("content", "")
            })
        
        return messages
    except Exception:
        return []


def test_supabase_connection() -> tuple[bool, str]:
    """
    測試 Supabase 連線
    
    Returns:
        tuple: (是否成功, 訊息)
    """
    client = get_supabase_client()
    if not client:
        url, key = get_supabase_config()
        if not url:
            return (False, "未找到 SUPABASE_URL（請檢查 Streamlit Secrets 或環境變數）")
        if not key:
            return (False, "未找到 SUPABASE_ANON_KEY（請檢查 Streamlit Secrets 或環境變數）")
        return (False, "無法建立 Supabase 客戶端")
    
    try:
        # 簡單查詢測試（嘗試讀取 conversations 表）
        result = client.table("conversations").select("id").limit(1).execute()
        return (True, "Supabase 連線成功，conversations 表可訪問")
    except Exception as e:
        error_msg = str(e)
        if "relation" in error_msg.lower() or "does not exist" in error_msg.lower():
            return (False, "Supabase 連線成功，但 conversations 表不存在（請先執行 SQL 建立表）")
        return (False, f"Supabase 連線失敗：{error_msg}")


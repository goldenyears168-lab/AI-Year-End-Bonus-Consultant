# utils/gemini_client.py
import google.generativeai as genai
import os
from dotenv import load_dotenv
import streamlit as st

# 自動判斷是本地開發還是雲端
load_dotenv()

def get_api_key():
    """
    獲取 API Key，優先使用 Streamlit Secrets（雲端），其次使用環境變數（本地）
    """
    # 優先使用 Streamlit Secrets（適用於 Streamlit Cloud）
    try:
        if hasattr(st, 'secrets') and st.secrets:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
            if api_key:
                return api_key
    except Exception:
        pass  # 如果 st.secrets 不可用（非 Streamlit 環境），繼續嘗試環境變數
    
    # 其次使用環境變數（適用於本地開發）
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        return api_key
    
    # 如果都找不到，返回 None
    return None

def call_gemini_logic(system_prompt, user_message, history=[], model="gemini-2.0-flash-exp", temperature=0.7, max_tokens=2000):
    """
    呼叫 Gemini API 的統一入口
    
    Args:
        system_prompt: 系統提示詞
        user_message: 用戶訊息
        history: List[Dict] 格式的對話歷史，格式為 [{"role": "user/assistant", "content": "..."}]
        model: 模型名稱，預設 gemini-2.0-flash-exp
        temperature: 創造力參數，0.0-1.0
        max_tokens: 最大輸出長度
    
    Returns:
        str: AI 回應內容，或錯誤訊息
    """
    # 動態獲取 API Key（每次調用時重新讀取，確保使用最新的 Secrets）
    api_key = get_api_key()
    if not api_key:
        return "⚠️ 錯誤：未找到 GEMINI_API_KEY。請檢查 Streamlit Secrets 或 .env 檔案。"
    
    try:
        # 每次調用時重新配置（確保使用最新的 API Key）
        genai.configure(api_key=api_key)
        # 使用 system_instruction 參數設定系統提示詞
        model_instance = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        
        # 建立聊天會話，直接使用歷史對話
        # Gemini API 的 history 格式需要是 List[Dict] 其中 role 為 "user" 或 "model"
        gemini_history = []
        for msg in history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                gemini_history.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                gemini_history.append({"role": "model", "parts": [content]})
        
        chat = model_instance.start_chat(history=gemini_history)
        
        # 發送當前用戶訊息並取得回應
        response = chat.send_message(user_message)
        return response.text
        
    except Exception as e:
        return f"⚠️ AI 連線錯誤: {str(e)}"


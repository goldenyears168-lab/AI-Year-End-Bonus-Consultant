# utils/gemini_client.py
import google.generativeai as genai
import os
from dotenv import load_dotenv
import streamlit as st

# 自動判斷是本地開發還是雲端
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    raise ValueError("未找到 GEMINI_API_KEY，請檢查 .env 或 Streamlit Secrets")

genai.configure(api_key=api_key)

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
    try:
        # 使用 system_instruction 參數設定系統提示詞
        model_instance = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        
        # 建立聊天會話
        chat = model_instance.start_chat(history=[])
        
        # 加入歷史對話（按順序發送用戶訊息，Gemini 會自動管理對話歷史）
        for msg in history:
            if msg.get("role") == "user":
                chat.send_message(msg.get("content", ""))
            # 注意：助手回應會自動記錄在 ChatSession 中，不需要手動加入
        
        # 發送當前用戶訊息並取得回應
        response = chat.send_message(user_message)
        return response.text
        
    except Exception as e:
        return f"⚠️ AI 連線錯誤: {str(e)}"


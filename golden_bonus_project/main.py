# main.py
import streamlit as st
from nodes.advisor import AdvisorNode
from core.pipeline import Pipeline
from config.settings import PAGE_TITLE, PAGE_HEADER

# 1. 頁面設定
st.set_page_config(page_title=PAGE_TITLE, layout="wide")
st.title(PAGE_HEADER)

# 2. 狀態初始化
if "messages" not in st.session_state:
    st.session_state.messages = []  # 用來存對話歷史

# 3. 初始化 Pipeline（只包含 AdvisorNode）
@st.cache_resource
def get_pipeline():
    pipe = Pipeline()
    pipe.add_node(AdvisorNode("Advisor"))
    return pipe

pipeline = get_pipeline()

# 4. 對話機器人介面
st.markdown("---")
st.subheader("💬 年終獎金顧問對話機器人")
st.info("💡 **使用提示**：您可以詢問任何關於年終獎金發放策略的問題，AI 顧問會根據專業知識庫為您提供建議。")

# 顯示歷史對話
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# 處理用戶輸入
if prompt := st.chat_input("請輸入您的問題... (例如：年終獎金應該如何分配？)"):
    # 1. 將用戶訊息加入對話歷史
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. 顯示用戶訊息
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 3. 準備聊天用的 context
    chat_context = {
        "current_intent": "CHAT",
        "latest_user_question": prompt,
        "history": [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages[:-1]  # 排除最後一條（剛加入的用戶訊息）
        ]
    }
    
    # 4. 執行 AdvisorNode
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("AI 思考中..."):
            try:
                # 執行聊天 Pipeline
                result_context = pipeline.run(chat_context)
                
                # 5. 顯示 AI 回應
                ai_response = result_context.get("ai_response", "抱歉，我無法回答這個問題。")
                st.markdown(ai_response)
                
                # 6. 將 AI 回應加入對話歷史
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response
                })
                
            except Exception as e:
                error_msg = f"⚠️ 系統錯誤：{str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

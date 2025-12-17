# main.py
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

# 側邊欄：AI 連線狀態（不顯示敏感資訊）
with st.sidebar:
    st.markdown("### 🔌 AI 連線狀態")
    try:
        from utils.gemini_client import get_api_key_source, test_gemini_connection

        key_source = get_api_key_source()
        st.caption(f"Key 來源：{key_source or '未設定'}")

        if st.button("測試 Gemini 連線", use_container_width=True):
            ok, msg = test_gemini_connection()
            if ok:
                st.success(msg)
            else:
                st.error(msg)

        if st.button("清除快取 / 重建 Pipeline", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
    except Exception as e:
        st.warning(f"無法載入連線檢查：{str(e)}")

# 側邊欄：企業補充資訊（用於後續提問的上下文）
with st.sidebar:
    st.markdown("### 🧾 企業補充資訊")
    if "company_context_text" not in st.session_state:
        st.session_state.company_context_text = ""

    if st.session_state.company_context_text:
        st.caption("已載入（後續提問會自動套用）")
        if st.button("清除補充資訊", use_container_width=True):
            st.session_state.company_context_text = ""
            st.rerun()
    else:
        st.caption("尚未貼上")

# 2. 狀態初始化
if "messages" not in st.session_state:
    st.session_state.messages = []  # 用來存對話歷史

# 3. 初始化 Pipeline（只包含 AdvisorNode）
@st.cache_resource
def get_pipeline(_cache_version: str):
    pipe = Pipeline()
    pipe.add_node(AdvisorNode("Advisor"))
    return pipe

pipeline = get_pipeline(PIPELINE_CACHE_VERSION)

# 4. 對話機器人介面
st.markdown("---")
st.subheader("💬 年終獎金顧問對話機器人")
st.info("💡 **使用提示**：您可以詢問任何關於年終獎金發放策略的問題，AI 顧問會根據專業知識庫為您提供建議。")

# 顯示歷史對話
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# 處理用戶輸入
if prompt := st.chat_input("請輸入您的問題或是貼上參考資訊... (例如：公司報告、問卷結果、討論紀錄等)"):
    # A) 若使用者貼的是公司補充資訊：先儲存，避免立刻進入顧問回覆
    if looks_like_company_report_payload(prompt):
        st.session_state.company_context_text = prompt
        receipt_msg = "已收到企業補充資訊，後續提問將以此作為背景資料。以下先提供一段依知識庫框架的原理解讀。"
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(receipt_msg)
        st.session_state.messages.append({"role": "assistant", "content": receipt_msg})

        # 立即輸出回饋：用「原理解讀模式」解說補充資訊（不需使用者再問一次）
        auto_context = {
            "current_intent": "CHAT_FOLLOWUP",
            "latest_user_question": "請用知識庫框架解說這份企業補充資訊的推導與解讀，全中文，不要給建議，不要反問。",
            "company_context_text": st.session_state.company_context_text,
            "history": [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.messages
            ],
        }
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("AI 思考中..."):
                try:
                    result_context = pipeline.run(auto_context)
                    ai_response = result_context.get("ai_response", "（已收到補充資訊，但暫時無法生成解說內容）")
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                except Exception as e:
                    error_msg = f"⚠️ 系統錯誤：{str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        st.stop()

    # 1. 將用戶訊息加入對話歷史
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. 顯示用戶訊息
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 3. 準備聊天用的 context
    chat_context = {
        "current_intent": "CHAT",
        "latest_user_question": prompt,
        "company_context_text": st.session_state.get("company_context_text", ""),
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

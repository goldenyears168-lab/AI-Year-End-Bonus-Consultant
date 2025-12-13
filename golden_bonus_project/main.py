# main.py
import streamlit as st
from core.pipeline import Pipeline
from nodes.calculator import CalculatorNode
from nodes.advisor import AdvisorNode

# 💡 配置中心：從集中配置檔案讀取所有可調整內容
from config.settings import (
    FORM_FIELDS, 
    QUICK_QUESTIONS, 
    BUTTON_LABELS, 
    PAGE_TITLE, 
    PAGE_HEADER,
    STYLE_DESCRIPTIONS
)

# 1. 頁面設定（從配置中心讀取）
st.set_page_config(page_title=PAGE_TITLE, layout="wide")
st.title(PAGE_HEADER)

# 2. 狀態初始化
if "pipeline_context" not in st.session_state:
    st.session_state.pipeline_context = {}  # 用來存計算結果
if "messages" not in st.session_state:
    st.session_state.messages = []          # 用來存對話歷史
if "data_changed" not in st.session_state:
    st.session_state.data_changed = False   # 追蹤數據是否變動

# 定義一個回調函數，當數據改變時清空緩存
def reset_on_change():
    """
    流程顧問原則：數據變動時必須清空所有緩存，並標記數據已變動。
    這樣可以強迫用戶重新生成報告，確保決策基於最新數據。
    """
    st.session_state.pipeline_context = {}  # 清空 Pipeline 結果
    st.session_state.messages = []  # 清空對話歷史
    st.session_state.data_changed = True  # ⚠️ 關鍵：標記數據已變動

# 3. 初始化 Pipeline (這就是我們的工廠)
# 透過 st.cache_resource 確保工廠只會被建立一次，不會每次按按鈕都重蓋
# 精實方案：只有 2 個節點（Calculator 已包含風險檢查）
@st.cache_resource
def get_pipeline():
    pipe = Pipeline()
    pipe.add_node(CalculatorNode("Calculator"))  # 包含計算 + 風險檢查
    pipe.add_node(AdvisorNode("Advisor"))       # AI 顧問建議
    return pipe

pipeline = get_pipeline()

# 4. 側邊欄輸入 (Input Layer) - 從配置中心讀取欄位定義
with st.sidebar:
    st.title("🎯 CEO 決策槓桿")
    
    # 槓桿 1：生存槓桿
    st.subheader("🛡️ 生存槓桿 (Safety Margin)")
    retention = st.slider(
        FORM_FIELDS["retention"]["label"],
        min_value=FORM_FIELDS["retention"]["min_value"],
        max_value=FORM_FIELDS["retention"]["max_value"],
        value=FORM_FIELDS["retention"]["default"],
        help=FORM_FIELDS["retention"]["help"],
        on_change=reset_on_change
    )
    
    st.markdown("---")
    
    # 槓桿 2：激勵槓桿
    st.subheader("🚀 激勵槓桿 (Motivation Strategy)")
    style = st.radio(
        FORM_FIELDS["style"]["label"],
        options=FORM_FIELDS["style"]["options"],
        help=FORM_FIELDS["style"]["help"]
    )
    # 顯示策略說明（從配置中心讀取）
    st.caption(STYLE_DESCRIPTIONS[style])
    
    st.markdown("---")
    
    # 槓桿 3：現實槓桿
    st.subheader("💰 現實槓桿 (Financial Reality)")
    st.caption("請輸入公司的財務底氣")
    
    revenue = st.number_input(
        FORM_FIELDS["revenue"]["label"],
        value=FORM_FIELDS["revenue"]["default"],
        step=FORM_FIELDS["revenue"]["step"],
        on_change=reset_on_change
    )
    net_profit = st.number_input(
        FORM_FIELDS["net_profit"]["label"],
        value=FORM_FIELDS["net_profit"]["default"],
        step=FORM_FIELDS["net_profit"]["step"],
        help=FORM_FIELDS["net_profit"]["help"],
        on_change=reset_on_change
    )
    employees = st.number_input(
        FORM_FIELDS["employees"]["label"],
        value=FORM_FIELDS["employees"]["default"],
        min_value=FORM_FIELDS["employees"]["min_value"],
        step=FORM_FIELDS["employees"]["step"],
        on_change=reset_on_change
    )
    avg_salary = st.number_input(
        FORM_FIELDS["avg_salary"]["label"],
        value=FORM_FIELDS["avg_salary"]["default"],
        min_value=FORM_FIELDS["avg_salary"]["min_value"],
        step=FORM_FIELDS["avg_salary"]["step"],
        on_change=reset_on_change
    )
    
    # 動態顯示存活月數（在所有欄位定義之後，不依賴 Pipeline）
    monthly_burn = employees * avg_salary
    if monthly_burn > 0:
        retained_amount = (net_profit * 10000) * (retention / 100.0)
        survival_months = retained_amount / monthly_burn
        st.caption(f"💡 靜態估算：約可支撐 {survival_months:.1f} 個月（精確分析請點擊「生成草案」）")
    
    start_btn = st.button(BUTTON_LABELS["generate"], type="primary", use_container_width=True)

# 5. 執行邏輯 (Controller Layer)
if start_btn:
    # 準備初始數據包
    initial_context = {
        "user_input": {
            "revenue": revenue,
            "net_profit": net_profit,
            "employees": employees,
            "avg_salary": avg_salary,
            "retention_rate": retention / 100.0, # 轉成小數
            "style": style
        },
        "current_intent": "GENERATE_REPORT"
    }
    
    # --- 關鍵時刻：啟動 Pipeline ---
    with st.spinner("AI 顧問大腦運算中..."):
        try:
            result_context = pipeline.run(initial_context)
            
            # ⚠️ 流程顧問提醒：生成報告後，清除「數據變動」標記
            # 這樣聊天功能才會重新啟用
            st.session_state.pipeline_context = result_context  # 保存結果
            st.session_state.data_changed = False  # 清除變動標記
            
            # 檢查是否有錯誤
            if "error" in result_context:
                st.error(f"❌ 計算錯誤：{result_context['error']}")
            else:
                # 6. 顯示結果 (View Layer)
                
                # 6.1 顯示 Metrics
                m = result_context["metrics"]
                col1, col2, col3 = st.columns(3)
                col1.metric("💰 總獎金池", f"{m['total_pool']:,} 元")
                col2.metric("👤 人均金額", f"{m['per_head']:,} 元")
                
                # 月數顯示（如果 < 0.5，顯示紅色字體警告）
                delta_color = "normal"
                if m['months'] < 0.5:
                    delta_color = "inverse"  # 紅色警告
                
                col3.metric("📅 平均月數", f"{m['months']} 個月", delta_color=delta_color)
                
                # 6.2 顯示 AI 建議
                st.markdown("---")
                st.subheader("📋 決策備忘錄 (Executive Memo)")
                
                with st.container(border=True):
                    st.markdown(result_context["ai_response"])
                
                # 6.3 顯示 Prompt (開發模式用，讓你看 AI 到底讀了什麼)
                with st.expander("🔧 開發者視角 (Debug Info)"):
                    st.text(result_context.get("system_prompt", ""))
                    
        except Exception as e:
            st.error(f"⚠️ 系統錯誤：{str(e)}")

# 7. 互動諮詢區 (Chat Interface)
st.markdown("---")
st.subheader("💬 互動諮詢區")

# 快捷追問按鈕（從配置中心讀取）
col1, col2, col3 = st.columns(3)
quick_question = None

if col1.button(QUICK_QUESTIONS["analyze_risks"]["label"], use_container_width=True):
    quick_question = QUICK_QUESTIONS["analyze_risks"]["question"]

if col2.button(QUICK_QUESTIONS["generate_scripts"]["label"], use_container_width=True):
    quick_question = QUICK_QUESTIONS["generate_scripts"]["question"]

if col3.button(QUICK_QUESTIONS["adjust_strategy"]["label"], use_container_width=True):
    quick_question = QUICK_QUESTIONS["adjust_strategy"]["question"]

# 顯示歷史對話
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# 處理快捷按鈕或聊天輸入
user_input = None
if quick_question:
    user_input = quick_question
elif prompt := st.chat_input("請輸入您的問題... (例如：如果不發給新人會違反勞基法嗎？)"):
    user_input = prompt

# 如果有用戶輸入，處理聊天邏輯
if user_input:
    # 1. 將用戶訊息加入對話歷史
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 2. 顯示用戶訊息
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 3. 準備聊天用的 context（使用已存在的 pipeline_context）
    chat_context = st.session_state.pipeline_context.copy()
    
    # 4. ⚠️ 流程顧問的雙重檢查：確保數據一致性和完整性
    # 檢查 1：數據是否已變動但未重新生成
    if st.session_state.get("data_changed", False):
        with st.chat_message("assistant", avatar="🤖"):
            st.error("⚠️ **數據已變更**：請先點擊「生成分配草案」按鈕更新分析，才能開始聊天。")
            st.info("💡 這是為了確保 AI 的回答基於最新的財務數據，避免決策錯誤。")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "數據已變更，請先重新生成報告。"
            })
    # 檢查 2：是否有計算結果
    elif "metrics" not in chat_context or not chat_context.get("metrics"):
        with st.chat_message("assistant", avatar="🤖"):
            st.warning("⚠️ 請先點擊「生成分配草案」按鈕，讓 AI 先分析您的數據。")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "請先點擊「生成分配草案」按鈕，讓 AI 先分析您的數據。"
            })
    else:
        # 5. 設定聊天意圖
        chat_context["current_intent"] = "CHAT_FOLLOWUP"
        chat_context["latest_user_question"] = user_input
        
        # 6. 將對話歷史轉換為 Gemini 格式
        chat_context["history"] = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages[:-1]  # 排除最後一條（剛加入的用戶訊息）
        ]
        
        # 7. 只執行 AdvisorNode（跳過 Calculator，使用已存在的 context）
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("AI 思考中..."):
                try:
                    # 建立一個只包含 AdvisorNode 的臨時 Pipeline
                    chat_pipeline = Pipeline()
                    chat_pipeline.add_node(AdvisorNode("Advisor"))
                    
                    # 執行聊天 Pipeline
                    result_context = chat_pipeline.run(chat_context)
                    
                    # 8. 顯示 AI 回應
                    ai_response = result_context.get("ai_response", "抱歉，我無法回答這個問題。")
                    st.markdown(ai_response)
                    
                    # 9. 將 AI 回應加入對話歷史
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


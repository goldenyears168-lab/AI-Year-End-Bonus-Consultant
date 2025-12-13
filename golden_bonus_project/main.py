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
    STYLE_DESCRIPTIONS,
    QUICK_PRESETS
)

# 1. 頁面設定（從配置中心讀取）
st.set_page_config(page_title=PAGE_TITLE, layout="wide")
st.title(PAGE_HEADER)

# 2. 狀態初始化（必須在配置區之前初始化）
if "pipeline_context" not in st.session_state:
    st.session_state.pipeline_context = {}  # 用來存計算結果
if "messages" not in st.session_state:
    st.session_state.messages = []          # 用來存對話歷史
if "data_changed" not in st.session_state:
    st.session_state.data_changed = False   # 追蹤數據是否變動
if "selected_preset" not in st.session_state:
    st.session_state.selected_preset = None  # 追蹤選擇的快速预设
# 配置值統一存儲（用於主內容區和側邊欄同步）
if "config_retention" not in st.session_state:
    st.session_state.config_retention = FORM_FIELDS["retention"]["default"]
if "config_style" not in st.session_state:
    st.session_state.config_style = FORM_FIELDS["style"]["options"][0]
if "config_net_profit" not in st.session_state:
    st.session_state.config_net_profit = FORM_FIELDS["net_profit"]["default"]
if "config_employees" not in st.session_state:
    st.session_state.config_employees = FORM_FIELDS["employees"]["default"]
if "config_avg_salary" not in st.session_state:
    st.session_state.config_avg_salary = FORM_FIELDS["avg_salary"]["default"]

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

# 4. 主內容區配置（手機版可見，預設展開）
st.markdown("---")
st.subheader("⚙️ CEO 決策槓桿配置")
st.info("💡 **使用提示**：調整以下參數來設定年終獎金分配策略。參數調整後，記得點擊下方的「生成分配草案」按鈕來更新分析結果。")

with st.expander("🎯 展開配置面板", expanded=True):
    # 快速预设功能
    st.subheader("⚡ 快速预设")
    preset_cols_main = st.columns(3)
    
    for idx, (preset_key, preset_data) in enumerate(QUICK_PRESETS.items()):
        with preset_cols_main[idx]:
            button_type = "primary" if st.session_state.selected_preset == preset_key else "secondary"
            if st.button(preset_data["label"], use_container_width=True, key=f"preset_main_{preset_key}", type=button_type):
                st.session_state.selected_preset = preset_key
                # 套用预设值到配置
                st.session_state.config_retention = preset_data["retention"]
                st.session_state.config_style = preset_data["style"]
                reset_on_change()
                st.rerun()
    
    if st.session_state.selected_preset:
        preset_data = QUICK_PRESETS[st.session_state.selected_preset]
        st.info(f"✅ 已套用：{preset_data['label']} - {preset_data['description']}")
    
    st.markdown("---")
    
    # 槓桿 1：生存槓桿
    st.subheader("🛡️ 生存槓桿 (Safety Margin)")
    
    # 如果选择了预设，使用预设值，否则使用session_state中的值
    initial_retention_main = QUICK_PRESETS[st.session_state.selected_preset]["retention"] if st.session_state.selected_preset else st.session_state.config_retention
    
    def clear_preset_on_change_main():
        reset_on_change()
        if st.session_state.selected_preset:
            st.session_state.selected_preset = None
    
    def update_retention_main():
        st.session_state.config_retention = st.session_state.retention_main
        clear_preset_on_change_main()
    
    retention_main = st.slider(
        FORM_FIELDS["retention"]["label"],
        min_value=FORM_FIELDS["retention"]["min_value"],
        max_value=FORM_FIELDS["retention"]["max_value"],
        value=initial_retention_main,
        help=FORM_FIELDS["retention"]["help"],
        key="retention_main",
        on_change=update_retention_main
    )
    st.session_state.config_retention = retention_main
    
    # 增强反馈：风险等级指示
    if retention_main >= 85:
        st.warning("⚠️ **高保留模式**：保留 85% 以上可能反映對未來的不安全感，建議釋放部分作為試錯基金。")
    elif retention_main >= 70:
        st.success("✅ **穩健型**：保留比例適中，平衡風險與激勵。")
    elif retention_main >= 50:
        st.info("💡 **成長型**：保留比例較低，更多資源回饋團隊，適合快速擴張期。")
    else:
        st.warning("⚠️ **激進型**：保留比例低於 50%，請確保公司現金流充足。")
    
    st.markdown("---")
    
    # 槓桿 2：激勵槓桿
    st.subheader("🚀 激勵槓桿 (Motivation Strategy)")
    
    initial_style_main = QUICK_PRESETS[st.session_state.selected_preset]["style"] if st.session_state.selected_preset else st.session_state.config_style
    style_index_main = FORM_FIELDS["style"]["options"].index(initial_style_main) if initial_style_main in FORM_FIELDS["style"]["options"] else 0
    
    def update_style_main():
        st.session_state.config_style = st.session_state.style_main
        clear_preset_on_change_main()
    
    style_main = st.radio(
        FORM_FIELDS["style"]["label"],
        options=FORM_FIELDS["style"]["options"],
        index=style_index_main,
        help=FORM_FIELDS["style"]["help"],
        key="style_main",
        on_change=update_style_main
    )
    st.session_state.config_style = style_main
    st.caption(STYLE_DESCRIPTIONS[style_main])
    
    st.markdown("---")
    
    # 槓桿 3：現實槓桿
    st.subheader("💰 現實槓桿 (Financial Reality)")
    st.caption("請輸入公司的財務底氣")
    
    def update_net_profit_main():
        st.session_state.config_net_profit = st.session_state.net_profit_main
        reset_on_change()
    
    net_profit_main = st.number_input(
        FORM_FIELDS["net_profit"]["label"],
        value=st.session_state.config_net_profit,
        step=FORM_FIELDS["net_profit"]["step"],
        help=FORM_FIELDS["net_profit"]["help"],
        key="net_profit_main",
        on_change=update_net_profit_main
    )
    st.session_state.config_net_profit = net_profit_main
    
    def update_employees_main():
        st.session_state.config_employees = st.session_state.employees_main
        reset_on_change()
    
    employees_main = st.number_input(
        FORM_FIELDS["employees"]["label"],
        value=st.session_state.config_employees,
        min_value=FORM_FIELDS["employees"]["min_value"],
        step=FORM_FIELDS["employees"]["step"],
        key="employees_main",
        on_change=update_employees_main
    )
    st.session_state.config_employees = employees_main
    
    def update_avg_salary_main():
        st.session_state.config_avg_salary = st.session_state.avg_salary_main
        reset_on_change()
    
    avg_salary_main = st.number_input(
        FORM_FIELDS["avg_salary"]["label"],
        value=st.session_state.config_avg_salary,
        min_value=FORM_FIELDS["avg_salary"]["min_value"],
        step=FORM_FIELDS["avg_salary"]["step"],
        key="avg_salary_main",
        on_change=update_avg_salary_main
    )
    st.session_state.config_avg_salary = avg_salary_main
    
    # 動態顯示存活月數
    monthly_burn_main = employees_main * avg_salary_main
    if monthly_burn_main > 0:
        retained_amount_main = (net_profit_main * 10000) * (retention_main / 100.0)
        survival_months_main = retained_amount_main / monthly_burn_main
        
        if survival_months_main >= 6:
            st.success(f"✅ **財務健康**：約可支撐 {survival_months_main:.1f} 個月（建議至少 6 個月）")
        elif survival_months_main >= 3:
            st.info(f"💡 **財務穩健**：約可支撐 {survival_months_main:.1f} 個月（精確分析請點擊「生成草案」）")
        else:
            st.warning(f"⚠️ **財務警告**：僅可支撐 {survival_months_main:.1f} 個月，低於建議的 6 個月安全線")
    
    start_btn_main = st.button(BUTTON_LABELS["generate"], type="primary", use_container_width=True, key="start_btn_main")

st.markdown("---")

# 5. 側邊欄輸入 (Input Layer) - 從配置中心讀取欄位定義（桌面版使用）
with st.sidebar:
    st.info("📱 **手機用戶提示**：配置區已移至主頁面頂部，預設展開。此側邊欄為桌面版額外選項，可摺疊。")
    st.markdown("---")
    st.title("🎯 CEO 決策槓桿（桌面版）")
    
    # 快速预设功能
    st.subheader("⚡ 快速预设")
    preset_cols = st.columns(3)
    
    for idx, (preset_key, preset_data) in enumerate(QUICK_PRESETS.items()):
        with preset_cols[idx]:
            # 高亮显示当前选择的预设
            button_type = "primary" if st.session_state.selected_preset == preset_key else "secondary"
            if st.button(preset_data["label"], use_container_width=True, key=f"preset_sidebar_{preset_key}", type=button_type):
                st.session_state.selected_preset = preset_key
                # 套用预设值到配置
                st.session_state.config_retention = preset_data["retention"]
                st.session_state.config_style = preset_data["style"]
                reset_on_change()
                st.rerun()
    
    if st.session_state.selected_preset:
        preset_data = QUICK_PRESETS[st.session_state.selected_preset]
        st.info(f"✅ 已套用：{preset_data['label']} - {preset_data['description']}")
    
    st.markdown("---")
    
    # 槓桿 1：生存槓桿
    st.subheader("🛡️ 生存槓桿 (Safety Margin)")
    
    # 如果选择了预设，使用预设值，否则使用session_state中的值
    initial_retention_sidebar = QUICK_PRESETS[st.session_state.selected_preset]["retention"] if st.session_state.selected_preset else st.session_state.config_retention
    
    # 定义回调函数：手动调整时清除预设选择
    def clear_preset_on_change_sidebar():
        reset_on_change()
        if st.session_state.selected_preset:
            st.session_state.selected_preset = None
    
    def update_retention_sidebar():
        st.session_state.config_retention = st.session_state.retention_sidebar
        clear_preset_on_change_sidebar()
    
    retention_sidebar = st.slider(
        FORM_FIELDS["retention"]["label"],
        min_value=FORM_FIELDS["retention"]["min_value"],
        max_value=FORM_FIELDS["retention"]["max_value"],
        value=initial_retention_sidebar,
        help=FORM_FIELDS["retention"]["help"],
        key="retention_sidebar",
        on_change=update_retention_sidebar
    )
    st.session_state.config_retention = retention_sidebar
    
    # 增强反馈：风险等级指示
    if retention_sidebar >= 85:
        st.warning("⚠️ **高保留模式**：保留 85% 以上可能反映對未來的不安全感，建議釋放部分作為試錯基金。")
    elif retention_sidebar >= 70:
        st.success("✅ **穩健型**：保留比例適中，平衡風險與激勵。")
    elif retention_sidebar >= 50:
        st.info("💡 **成長型**：保留比例較低，更多資源回饋團隊，適合快速擴張期。")
    else:
        st.warning("⚠️ **激進型**：保留比例低於 50%，請確保公司現金流充足。")
    
    st.markdown("---")
    
    # 槓桿 2：激勵槓桿
    st.subheader("🚀 激勵槓桿 (Motivation Strategy)")
    
    # 如果选择了预设，使用预设值，否则使用session_state中的值
    initial_style_sidebar = QUICK_PRESETS[st.session_state.selected_preset]["style"] if st.session_state.selected_preset else st.session_state.config_style
    style_index_sidebar = FORM_FIELDS["style"]["options"].index(initial_style_sidebar) if initial_style_sidebar in FORM_FIELDS["style"]["options"] else 0
    
    def update_style_sidebar():
        st.session_state.config_style = st.session_state.style_sidebar
        clear_preset_on_change_sidebar()
    
    style_sidebar = st.radio(
        FORM_FIELDS["style"]["label"],
        options=FORM_FIELDS["style"]["options"],
        index=style_index_sidebar,
        help=FORM_FIELDS["style"]["help"],
        key="style_sidebar",
        on_change=update_style_sidebar
    )
    st.session_state.config_style = style_sidebar
    # 顯示策略說明（從配置中心讀取）
    st.caption(STYLE_DESCRIPTIONS[style_sidebar])
    
    st.markdown("---")
    
    # 槓桿 3：現實槓桿
    st.subheader("💰 現實槓桿 (Financial Reality)")
    st.caption("請輸入公司的財務底氣")
    
    def update_net_profit_sidebar():
        st.session_state.config_net_profit = st.session_state.net_profit_sidebar
        reset_on_change()
    
    net_profit_sidebar = st.number_input(
        FORM_FIELDS["net_profit"]["label"],
        value=st.session_state.config_net_profit,
        step=FORM_FIELDS["net_profit"]["step"],
        help=FORM_FIELDS["net_profit"]["help"],
        key="net_profit_sidebar",
        on_change=update_net_profit_sidebar
    )
    st.session_state.config_net_profit = net_profit_sidebar
    
    def update_employees_sidebar():
        st.session_state.config_employees = st.session_state.employees_sidebar
        reset_on_change()
    
    employees_sidebar = st.number_input(
        FORM_FIELDS["employees"]["label"],
        value=st.session_state.config_employees,
        min_value=FORM_FIELDS["employees"]["min_value"],
        step=FORM_FIELDS["employees"]["step"],
        key="employees_sidebar",
        on_change=update_employees_sidebar
    )
    st.session_state.config_employees = employees_sidebar
    
    def update_avg_salary_sidebar():
        st.session_state.config_avg_salary = st.session_state.avg_salary_sidebar
        reset_on_change()
    
    avg_salary_sidebar = st.number_input(
        FORM_FIELDS["avg_salary"]["label"],
        value=st.session_state.config_avg_salary,
        min_value=FORM_FIELDS["avg_salary"]["min_value"],
        step=FORM_FIELDS["avg_salary"]["step"],
        key="avg_salary_sidebar",
        on_change=update_avg_salary_sidebar
    )
    st.session_state.config_avg_salary = avg_salary_sidebar
    
    # 動態顯示存活月數（在所有欄位定義之後，不依賴 Pipeline）
    monthly_burn_sidebar = employees_sidebar * avg_salary_sidebar
    if monthly_burn_sidebar > 0:
        retained_amount_sidebar = (net_profit_sidebar * 10000) * (retention_sidebar / 100.0)
        survival_months_sidebar = retained_amount_sidebar / monthly_burn_sidebar
        
        # 增强反馈：根据存活月数显示不同颜色
        if survival_months_sidebar >= 6:
            st.success(f"✅ **財務健康**：約可支撐 {survival_months_sidebar:.1f} 個月（建議至少 6 個月）")
        elif survival_months_sidebar >= 3:
            st.info(f"💡 **財務穩健**：約可支撐 {survival_months_sidebar:.1f} 個月（精確分析請點擊「生成草案」）")
        else:
            st.warning(f"⚠️ **財務警告**：僅可支撐 {survival_months_sidebar:.1f} 個月，低於建議的 6 個月安全線")
    
    start_btn_sidebar = st.button(BUTTON_LABELS["generate"], type="primary", use_container_width=True, key="start_btn_sidebar")

# 6. 執行邏輯 (Controller Layer) - 統一從session_state讀取配置值
start_btn = start_btn_main or start_btn_sidebar  # 任一按鈕點擊都觸發

if start_btn:
    # 準備初始數據包（從session_state統一讀取配置值）
    initial_context = {
        "user_input": {
            # 已移除 revenue 字段，計算邏輯不依賴營收數據
            "net_profit": st.session_state.config_net_profit,
            "employees": st.session_state.config_employees,
            "avg_salary": st.session_state.config_avg_salary,
            "retention_rate": st.session_state.config_retention / 100.0, # 轉成小數
            "style": st.session_state.config_style
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
                # 7. 顯示結果 (View Layer)
                
                # 7.1 顯示 Metrics
                m = result_context["metrics"]
                col1, col2, col3 = st.columns(3)
                col1.metric("💰 總獎金池", f"{m['total_pool']:,} 元")
                col2.metric("👤 人均金額", f"{m['per_head']:,} 元")
                
                # 月數顯示（如果 < 0.5，顯示紅色字體警告）
                delta_color = "normal"
                if m['months'] < 0.5:
                    delta_color = "inverse"  # 紅色警告
                
                col3.metric("📅 平均月數", f"{m['months']} 個月", delta_color=delta_color)
                
                # 7.2 顯示 AI 建議
                st.markdown("---")
                st.subheader("📋 決策備忘錄 (Executive Memo)")
                
                with st.container(border=True):
                    st.markdown(result_context["ai_response"])
                
                # 7.3 顯示 Prompt (開發模式用，讓你看 AI 到底讀了什麼)
                with st.expander("🔧 開發者視角 (Debug Info)"):
                    st.text(result_context.get("system_prompt", ""))
                    
        except Exception as e:
            st.error(f"⚠️ 系統錯誤：{str(e)}")

# 8. 互動諮詢區 (Chat Interface)
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


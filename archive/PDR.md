我們採用 「MVC 變體架構」：

Model (數據層): 你的 Context 字典。

View (表現層): Streamlit 的介面。

Controller (邏輯層): 我們的 Pipeline 和 Nodes。

第一章：專案地圖 (The Territory)
首先，我們不要把所有程式碼塞在一個檔案裡。我們要建立一個標準的 Python 專案結構。請在你的 VS Code 裡建立這樣的資料夾：

Plaintext

golden_bonus_project/           # [根目錄] 專案起點
│
├── .env                        # [機密] 放 GEMINI_API_KEY=... (絕對不要上傳 GitHub)
├── requirements.txt            # [清單] 告訴電腦要安裝 streamlit, google-generativeai
├── main.py                     # [入口] 程式啟動點，只負責畫 UI
│
├── core/                       # [核心引擎] 這裡放通用的管線邏輯，以後別的專案也能用
│   ├── __init__.py             # (空檔案) 讓 Python 知道這是個套件包
│   ├── pipeline.py             # 定義「管線」怎麼跑
│   └── base_node.py            # 定義「節點」長什麼樣子 (父類別)
│
├── nodes/                      # [業務邏輯] 這裡放這次專案專屬的功能
│   ├── __init__.py
│   ├── calculator.py           # 節點 1: 負責算錢 + 風險檢查（精實方案）
│   └── advisor.py              # 節點 2: 負責跟 Gemini API 講話
│
├── assets/                     # [靜態資源]
│   └── knowledge.py            # 你的顧問知識庫文字檔
│
└── config/                     # [配置中心] 所有可調整的內容集中管理
    └── settings.py             # 表單欄位定義、知識庫路徑、提示詞等
CTO 的叮嚀： 為什麼要分這麼細？因為 main.py 應該只管「長相」，nodes/ 只管「思考」。這樣除錯時，如果是算錯錢，你只要去 calculator.py 找，不用在幾千行程式碼裡大海撈針。

第二章：數據契約 (The Bloodstream)
在我們的 Pipeline 裡流動的 context (上下文) 是整個系統的血液。新手常犯的錯是「隨意命名變數」。我們要嚴格定義這個 Dictionary 長什麼樣。

這是在每個節點之間傳遞的 context 字典結構：

Python

# 這是一個 Python Dictionary，它會在 Pipeline 中不斷變胖
context = {
    # --- 1. 原始輸入 (由 main.py 注入) ---
    "user_input": {
        "revenue": 10000000,      # 營收 (Int)
        "net_profit": 2000000,    # 淨利 (Int)
        "employees": 5,           # 員工數 (Int)
        "avg_salary": 40000,      # 平均月薪 (Int)
        "retention_rate": 0.7,    # 保留盈餘比例 (Float) 0.0 - 1.0，包含股東分潤與明年營運週轉金
        "style": "conservative"   # 風格 (Str)
    },

    # --- 2. 中間產物 (由 Calculator Node 產生) ---
    "metrics": {
        "total_pool": 600000,     # 獎金總池 (Int)
        "per_head": 120000,       # 人均金額 (Int)
        "months": 3.0             # 平均月數 (Float)
    },

    # --- 3. 風險評估 (由 Calculator Node 產生，精實方案) ---
    "risks": [                    # 這是一個 List，沒風險就是空的 []
        "⚠️ 嚴重警告：平均月數低於 0.5 個月，離職風險極高。"
    ],

    # --- 4. 最終輸出 (由 Advisor Node 產生) ---
    "ai_response": "根據您的數據...", # (Str) Markdown 格式
    "system_prompt": "你是專業顧問..." # (Str) 用於 Debug 查看 Prompt 組合是否正確
}
第三章：核心引擎實作 (The Engine Room)
這裡是最抽象、但也最強大的部分。我們要教 Python 什麼是「節點」。

3.1 定義節點規格 (core/base_node.py)
Python

# core/base_node.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseNode(ABC):
    """
    這是所有節點的「爸爸」（父類別）。
    它規定所有繼承它的「孩子」都必須會做 execute 這件事。
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        輸入：context (舊的)
        輸出：context (新的，加上這個節點處理後的結果)
        """
        pass
3.2 定義生產線 (core/pipeline.py)
Python

# core/pipeline.py
from typing import List, Dict, Any
from core.base_node import BaseNode

class Pipeline:
    def __init__(self):
        self.nodes: List[BaseNode] = [] # 準備一個空的清單來放節點

    def add_node(self, node: BaseNode):
        self.nodes.append(node)
        return self # 讓我們可以寫 .add().add() 這種鍊式語法

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("🚀 Pipeline 開始運作...")
        
        # 這是最關鍵的迴圈：像大隊接力一樣傳遞 context
        for node in self.nodes:
            try:
                print(f"   Running node: {node.name}")
                context = node.execute(context) # 接棒！
            except Exception as e:
                print(f"❌ Error in {node.name}: {e}")
                context["error"] = str(e) # 把錯誤記下來，不要讓程式崩潰
                break # 停止產線
        
        print("✅ Pipeline 完成")
        return context
第四章：業務邏輯實作 (The Workers)
現在我們要來寫真正做事的節點。這對應到你的**「Functional Spec」**。

4.1 計算節點 (nodes/calculator.py) - 精實方案

💡 **精實設計**：將風險檢查合併到計算節點，減少架構複雜度。

```python
# nodes/calculator.py
from core.base_node import BaseNode
from typing import Dict, Any

class CalculatorNode(BaseNode):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        data = context["user_input"]
        
        # 1. 安全檢查：避免除以零的錯誤 (Edge Case)
        if data["employees"] <= 0:
            raise ValueError("員工人數不能為 0")
        if data["avg_salary"] <= 0:
            raise ValueError("平均月薪不能為 0 或負數")

        # 2. 核心公式
        # 獎金池 = 淨利 * (1 - 保留比例)
        # 注意：保留比例包含股東分潤與明年營運週轉金（簡化模型）
        pool = data["net_profit"] * (1 - data["retention_rate"])
        
        # 人均 = 獎金池 / 人數
        per_head = pool / data["employees"]
        
        # 月數 = 人均 / 月薪
        months = per_head / data["avg_salary"]

        # 3. 寫入 Metrics
        context["metrics"] = {
            "total_pool": int(pool),
            "per_head": int(per_head),
            "months": round(months, 2) # 取小數點後兩位
        }
        
        # 4. 風險檢查（精實：直接在這裡檢查，不單獨建立節點）
        risks = []
        
        # 規則 1: 發太少 (低於 0.5 個月)
        if months < 0.5:
            risks.append("⚠️ **紅色警報**：平均獎金低於 0.5 個月，根據統計，這會導致年後離職率上升 30%。")
        
        # 規則 2: 發太多 (透支保留盈餘)
        # 假設我們不希望老闆保留盈餘低於 10%
        if data["retention_rate"] < 0.1:
            risks.append("⚠️ **財務警告**：您的保留盈餘過低，公司現金流抗風險能力將減弱。")
        
        context["risks"] = risks
        
        return context
```
4.2 風險檢查（已合併到 CalculatorNode）

💡 **精實設計決策**：

風險檢查已合併到 `CalculatorNode`，因為：
- 只有 2 條簡單規則（約 10 行代碼）
- 風險檢查依賴計算結果（`metrics`），邏輯緊密相關
- MVP 階段減少節點數量，降低架構複雜度

**未來擴展**：如果風險規則超過 5 條，或需要外部 API（例如查詢行業標準、法規合規），可以重構為獨立的 `RiskScannerNode`。

---

## 配置中心設計 (Configuration Center)

💡 **設計目標**：將所有可調整的內容（知識庫、表單欄位、提示詞等）集中到一個檔案，方便後續修改。

📄 **config/settings.py - 配置中心**：

```python
# config/settings.py
"""
配置中心：所有可調整的內容集中管理

修改原則：
1. 知識庫內容 → 修改 assets/knowledge.py 中的 BONUS_KB_TEXT
2. 表單欄位 → 修改本檔案中的 FORM_FIELDS
3. 提示詞模板 → 修改本檔案中的 PROMPT_TEMPLATES
4. 快捷按鈕問題 → 修改本檔案中的 QUICK_QUESTIONS

這樣就不需要在程式碼中到處搜尋散落的定義。
"""

# ==================== 知識庫配置 ====================
KNOWLEDGE_BASE_PATH = "assets.knowledge"
KNOWLEDGE_VARIABLE_NAME = "BONUS_KB_TEXT"  # 知識庫變數名稱

# ==================== 表單欄位定義 ====================
# 所有 Sidebar 的輸入欄位定義集中管理
FORM_FIELDS = {
    "revenue": {
        "label": "年度總營收 (萬元)",
        "default": 1000,
        "step": 10,
        "help": None
    },
    "net_profit": {
        "label": "稅前淨利 (萬元)",
        "default": 100,
        "step": 10,
        "help": "請扣除營業成本與費用，但在扣稅之前的金額。"
    },
    "employees": {
        "label": "符合發放資格人數",
        "default": 5,
        "min_value": 1,
        "step": 1,
        "help": None
    },
    "avg_salary": {
        "label": "平均月薪 (元)",
        "default": 40000,
        "min_value": 1,
        "step": 1000,
        "help": None
    },
    "retention": {
        "label": "公司安全氣囊 (%)",
        "default": 70,
        "min_value": 0,
        "max_value": 100,
        "help": "這筆保留盈餘能讓公司在零收入狀態下存活幾個月？數值越高，公司抗風險能力越強，但發給員工的越少。建議穩健型保留 70-80%。**注意：此保留比例包含股東分潤與明年營運週轉金。**"
    },
    "style": {
        "label": "人才投資策略",
        "options": [
            "留才優先 (Retention First)",
            "戰功優先 (Performance First)",
            "團隊優先 (Team First)"
        ],
        "help": "這決定了獎金池的分配邏輯。留才優先 = 穩健型（S級 1.5倍），戰功優先 = 激勵型（S級 2.0倍），團隊優先 = 普惠型（差距縮小）。"
    }
}

# 表單欄位的說明文字（顯示在選項下方）
STYLE_DESCRIPTIONS = {
    "留才優先 (Retention First)": "💡 策略：確保核心戰力不流失，適合穩定成長期",
    "戰功優先 (Performance First)": "💡 策略：重賞勇夫，建立績效文化，適合快速擴張期",
    "團隊優先 (Team First)": "💡 策略：人人有獎，強化團隊凝聚力，適合轉型期"
}

# ==================== 快捷按鈕問題 ====================
# 聊天區的快捷按鈕問題集中管理
QUICK_QUESTIONS = {
    "analyze_risks": {
        "label": "⚠️ 分析潛在風險",
        "question": "請詳細分析這個方案的潛在風險，包括財務風險和留才風險。"
    },
    "generate_scripts": {
        "label": "🗣️ 生成面談話術",
        "question": "請為我生成針對不同績效等級員工的面談話術，要具體、可執行。"
    },
    "adjust_strategy": {
        "label": "⚖️ 調整為激勵型",
        "question": "如果我想改為激勵型策略，獎金分配會如何變化？"
    }
}

# ==================== 提示詞模板 ====================
# System Prompt 的模板集中管理（方便調整語氣、格式等）
PROMPT_TEMPLATES = {
    "generate_report": """
你是一位年薪千萬的麥肯錫顧問，專門協助 CEO 制定年終獎金策略。

【知識庫】：{knowledge_base}
【企業數據】：營收 {revenue} 萬，淨利 {net_profit} 萬，風格 {style}
【計算結果】：總獎金池 {total_pool} 元，人均 {per_head} 元，平均 {months} 個月
【風險提示】：{risks}

**你的任務**：用「黃金三段式」輸出，每段不超過 3 句話。不要說客套話。

**輸出格式**（嚴格遵守）：

### 🎯 戰略判斷 (The Verdict)
[一句話總結：目前的財務結構適合什麼策略？]

### ⚖️ 取捨分析 (The Trade-off)
[明確指出：這個方案的風險是什麼？效益是什麼？老闆需要做什麼決定？]

### 💬 關鍵對話 (The Script)
[只給一句話，針對最重要的員工群體（通常是 S 級）]

**禁止事項**：
- 不要列出所有等級的獎金數字（那是計算器的活）
- 不要說「根據計算...」（直接給判斷）
- 不要超過一頁 A4 紙的長度
""",
    
    "chat_followup": """
你是一位專業的年終獎金顧問，正在與企業主進行一對一諮詢。

【知識庫】：{knowledge_base}
【當前企業數據】：
- 營收：{revenue} 萬
- 淨利：{net_profit} 萬
- 員工數：{employees} 人
- 平均月薪：{avg_salary} 元
- 管理風格：{style}

【已計算結果】：
- 總獎金池：{total_pool} 元
- 人均金額：{per_head} 元
- 平均月數：{months} 個月

【已知風險】：{risks}

**你的任務**：根據用戶的問題，提供具體、可執行的建議。回答要簡潔、直接，不要重複已經說過的內容。
"""
}

# ==================== 其他配置 ====================
# 按鈕文字
BUTTON_LABELS = {
    "generate": "🚀 開始分析 / 生成草案",
    "reset": "🗑️ 清除重置"
}

# 頁面標題
PAGE_TITLE = "GoldenBonus AI"
PAGE_HEADER = "🤖 GoldenBonus 年終獎金顧問"
```

4.3 AI 顧問節點 (nodes/advisor.py)
這裡我們模擬呼叫 AI，實際開發時你會在這裡 import google.generativeai。

💡 **配置中心設計**：知識庫和提示詞從 `config/settings.py` 讀取，方便後續修改。

```python
# nodes/advisor.py
from core.base_node import BaseNode
from config.settings import PROMPT_TEMPLATES  # 從配置中心讀取提示詞模板
from assets.knowledge import BONUS_KB_TEXT
from typing import Dict, Any

class AdvisorNode(BaseNode):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        intent = context.get("current_intent", "GENERATE_REPORT")
        user_data = context["user_input"]
        metrics = context.get("metrics", {})
        risks = "\n".join(context.get("risks", []))
        
        if intent == "GENERATE_REPORT":
            # 使用配置中心的提示詞模板
            system_prompt = PROMPT_TEMPLATES["generate_report"].format(
                knowledge_base=BONUS_KB_TEXT,
                revenue=user_data.get('revenue', 'N/A'),
                net_profit=user_data.get('net_profit', 'N/A'),
                style=user_data.get('style', 'N/A'),
                total_pool=metrics.get('total_pool', 'N/A'),
                per_head=metrics.get('per_head', 'N/A'),
                months=metrics.get('months', 'N/A'),
                risks=risks if risks else "無"
            )
            user_msg = "請根據上述數據，生成一份完整的年終獎金分配草案。"
        
        elif intent == "CHAT_FOLLOWUP":
            # 使用配置中心的聊天提示詞模板
            system_prompt = PROMPT_TEMPLATES["chat_followup"].format(
                knowledge_base=BONUS_KB_TEXT,
                revenue=user_data.get('revenue', 'N/A'),
                net_profit=user_data.get('net_profit', 'N/A'),
                employees=user_data.get('employees', 'N/A'),
                avg_salary=user_data.get('avg_salary', 'N/A'),
                style=user_data.get('style', 'N/A'),
                total_pool=metrics.get('total_pool', 'N/A'),
                per_head=metrics.get('per_head', 'N/A'),
                months=metrics.get('months', 'N/A'),
                risks=risks if risks else "無"
            )
            user_msg = context.get("latest_user_question", "")
        
        # 呼叫 Gemini API
        from utils.gemini_client import call_gemini_logic
        history = context.get("history", [])
        response = call_gemini_logic(system_prompt, user_msg, history)
        
        context["ai_response"] = response
        context["system_prompt"] = system_prompt
        
        return context
```
第五章：前端整合 (The Face)
最後，我們回到 main.py，用 Streamlit 把這些積木組起來。這對應到你的 User Flow。

💡 **配置中心設計**：所有表單欄位、快捷問題、提示詞都從 `config/settings.py` 讀取，方便後續修改。

```python
# main.py
import streamlit as st
from core.pipeline import Pipeline
from nodes.calculator import CalculatorNode
from nodes.advisor import AdvisorNode
# 精實方案：不需要 import RiskScannerNode，風險檢查已合併到 CalculatorNode

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

# 2. 初始化 Pipeline (這就是我們的工廠)
# 透過 st.cache_resource 確保工廠只會被建立一次，不會每次按按鈕都重蓋
# 精實方案：只有 2 個節點（Calculator 已包含風險檢查）
@st.cache_resource
def get_pipeline():
    pipe = Pipeline()
    pipe.add_node(CalculatorNode("Calculator"))  # 包含計算 + 風險檢查
    pipe.add_node(AdvisorNode("Advisor"))       # AI 顧問建議
    return pipe

pipeline = get_pipeline()

# 3. 側邊欄輸入 (Input Layer) - 從配置中心讀取欄位定義
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
    
    # 動態顯示存活月數（不依賴 Pipeline）
    # 注意：這裡需要先定義 employees 和 avg_salary，所以順序很重要
    # 或者可以將這段邏輯移到所有欄位定義之後
    
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
    
    # 動態顯示存活月數（在所有欄位定義之後）
    monthly_burn = employees * avg_salary
    if monthly_burn > 0:
        retained_amount = (net_profit * 10000) * (retention / 100.0)
        survival_months = retained_amount / monthly_burn
        st.caption(f"💡 靜態估算：約可支撐 {survival_months:.1f} 個月（精確分析請點擊「生成草案」）")
    
    start_btn = st.button(BUTTON_LABELS["generate"], type="primary", use_container_width=True)

# 4. 執行邏輯 (Controller Layer)
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
        }
    }
    
    # --- 關鍵時刻：啟動 Pipeline ---
    with st.spinner("AI 顧問大腦運算中..."):
        result_context = pipeline.run(initial_context)
        
        # ⚠️ 流程顧問提醒：生成報告後，清除「數據變動」標記
        # 這樣聊天功能才會重新啟用
        st.session_state.pipeline_context = result_context  # 保存結果
        st.session_state.data_changed = False  # 清除變動標記
    
    # 5. 顯示結果 (View Layer)
    
    # 5.1 顯示 Metrics
    m = result_context["metrics"]
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 總獎金池", f"{m['total_pool']:,} 元")
    col2.metric("👤 人均金額", f"{m['per_head']:,} 元")
    col3.metric("📅 平均月數", f"{m['months']} 個月")
    
    # 5.2 顯示 AI 建議
    st.markdown("---")
    st.subheader("📝 顧問建議書")
    st.markdown(result_context["ai_response"])
    
    # 5.3 顯示 Prompt (開發模式用，讓你看 AI 到底讀了什麼)
    with st.expander("🔧 開發者視角 (Debug Info)"):
        st.text(result_context["system_prompt"])

第六章：新手工程師的自我驗收清單
Jack，在你寫完上面的程式碼後，請按照這個清單自己檢查一遍，這就是資深工程師的 Quality Assurance (QA)：

[ ] 除以零測試： 在側邊欄把「員工數」改成 0，程式會崩潰還是會顯示友好的錯誤訊息？（我們的 CalculatorNode 有處理，但 Streamlit 層面可以再包一個 try-except）。

[ ] 負數測試： 如果「淨利」輸入 -100 萬（虧損），AI 會建議發獎金嗎？（你需要去優化 CalculatorNode 的邏輯，如果 pool < 0 就設為 0）。

[ ] 流程驗證： 使用 print() 大法。看終端機 (Terminal) 是否依序印出：

🚀 Pipeline 開始運作...

Running node: Calculator

Running node: Advisor




1. Gemini API 實作細節 (Real Implementation)
我們不能再用假資料了。這是 nodes/advisor.py 必須具備的真實邏輯。

模型選擇： 指定 gemini-2.0-flash-exp（Google 最新的 Flash 模型，速度快且成本低）。

參數設定： temperature=0.7（讓顧問有創造力但不過於發散）。

串流處理： 為了體驗好，建議開啟 stream=True，但在 MVP 階段為了 Pipeline 結構簡單，我們先用非串流（一次回傳），等下一版再優化。

📄 程式碼規格 (nodes/advisor.py 核心函數)：

```python
import os
import streamlit as st
import google.generativeai as genai

# 兼容本地開發 (.env) 與 雲端部署 (st.secrets)
def get_api_key():
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.getenv("GEMINI_API_KEY")

def call_gemini_logic(system_prompt, user_message, history=[]):
    """
    呼叫 Gemini 2.0 Flash API
    
    Args:
        system_prompt: 系統提示詞
        user_message: 用戶訊息
        history: 對話歷史，格式為 [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        str: AI 回應內容
    """
    api_key = get_api_key()
    if not api_key:
        return "⚠️ 未設定 GEMINI_API_KEY，請檢查 .env 或 Streamlit Secrets"
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        system_instruction=system_prompt
    )
    
    # 建立聊天會話
    chat = model.start_chat(history=[])
    
    # 加入歷史對話（按順序發送用戶訊息，Gemini 會自動管理對話歷史）
    for msg in history:
        if msg.get("role") == "user":
            chat.send_message(msg.get("content", ""))
        # 注意：助手回應會自動記錄在 ChatSession 中，不需要手動加入
    
    try:
        # 發送當前用戶訊息並取得回應
        response = chat.send_message(user_message)
        return response.text
    except Exception as e:
        return f"⚠️ AI 連線錯誤: {str(e)}"
```
2. 對話狀態的「縫合」邏輯 (State Management)
這是 Streamlit 最容易出 bug 的地方。當使用者在左邊改了數字，右邊的舊報告必須銷毀，否則會出現「營收變了，但建議沒變」的矛盾。

⚠️ **流程顧問的關鍵提醒**：決策必須基於最新數據。如果用戶調整了 Sidebar 數據但沒有重新生成報告，聊天功能必須被禁用，強迫用戶先點擊「生成草案」。

🔄 邏輯流程圖：

📄 程式碼規格 (請放在 main.py 最上方)：

```python
# 定義一個函數來檢查數據是否變動
def check_reset_condition(current_inputs):
    """
    檢查輸入數據是否變動，如果變動則清空所有緩存。
    
    流程顧問原則：決策必須基於最新數據。
    如果數據變動，必須強迫用戶重新生成報告，才能開始聊天。
    """
    # 如果這是第一次執行，初始化 snapshot
    if "input_snapshot" not in st.session_state:
        st.session_state.input_snapshot = current_inputs
        return False  # 沒有變動

    # 如果當前輸入與快照不同 -> 清空歷史
    if st.session_state.input_snapshot != current_inputs:
        # 清空所有緩存
        st.session_state.messages = []  # 清空對話歷史
        st.session_state.pipeline_context = {}  # 清空 Pipeline 結果
        st.session_state.input_snapshot = current_inputs  # 更新快照
        
        # 提示用戶（使用 toast 不會中斷流程）
        st.toast("⚠️ 數據已變更，請重新點擊「生成草案」以更新分析", icon="🔄")
        return True  # 有變動
    
    return False  # 沒有變動

# 在 main.py 收集完 sidebar 數據後，立刻呼叫此函數
current_inputs = {
    "revenue": revenue,
    "net_profit": net_profit,
    "employees": employees,
    "avg_salary": avg_salary,
    "retention_rate": retention,
    "style": style
}

data_changed = check_reset_condition(current_inputs)

# 如果數據變動，在聊天區顯示警告
if data_changed:
    st.session_state.data_changed = True
```

📄 **聊天區的數據同步檢查**（在互動諮詢區加入）：

```python
# 區域 4：互動諮詢區
st.markdown("---")
st.subheader("💬 互動諮詢區")

# ⚠️ 關鍵檢查：如果數據已變動但未重新生成，禁用聊天功能
if st.session_state.get("data_changed", False):
    st.warning("⚠️ **數據已變更**：請先點擊「生成分配草案」按鈕更新分析，才能開始聊天。")
    st.info("💡 這是為了確保 AI 的回答基於最新的財務數據，避免決策錯誤。")
    # 不顯示聊天輸入框，強迫用戶先重新生成
else:
    # 正常的聊天功能（只有在數據未變動或已重新生成時才顯示）
    # ... 聊天輸入框和快捷按鈕 ...
    
    # 額外檢查：即使 data_changed 為 False，也要確認 pipeline_context 存在
    if "metrics" not in st.session_state.get("pipeline_context", {}):
        st.info("💡 請先點擊「生成分配草案」按鈕，讓 AI 分析您的數據。")
    else:
        # 顯示完整的聊天功能
        # ... 快捷按鈕和聊天輸入 ...
```

💡 **流程顧問的設計原則**：

1. **數據一致性優先**：寧可禁用功能，也不能讓用戶基於過時數據做決策
2. **明確的用戶引導**：用警告和提示告訴用戶為什麼不能聊天，以及該怎麼做
3. **雙重檢查**：既檢查 `data_changed` 標記，也檢查 `pipeline_context` 是否存在
4. **友善的錯誤處理**：使用 `st.warning` 和 `st.info` 而非直接報錯
3. 聊天視窗的 Pipeline 觸發機制 (Intent Handling)
我們的 Pipeline 只有一條，但「入口」有兩個：

生成草案按鈕：意圖是 GENERATE_REPORT。

聊天輸入框：意圖是 CHAT_FOLLOWUP。

我們需要在 Context 中加入 intent 欄位，讓 AdvisorNode 知道該怎麼做。

📄 **完整的互動聊天功能實作** (main.py 聊天區塊)：

```python
# main.py - 區域 4：互動諮詢區

# 初始化對話歷史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 初始化 context（用於聊天時參考）
if "pipeline_context" not in st.session_state:
    st.session_state.pipeline_context = {}

# 顯示聊天標題
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
```

📄 **nodes/advisor.py 的完整判斷邏輯**：

```python
class AdvisorNode(BaseNode):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        intent = context.get("current_intent", "GENERATE_REPORT")
        
        # 取得知識庫
        from assets.knowledge import BONUS_KB_TEXT
        
        if intent == "GENERATE_REPORT":
            # 模式 A：生成完整報告（需要完整 Pipeline）
            # 確保 CalculatorNode 已執行（已包含風險檢查）
            if "metrics" not in context:
                raise ValueError("計算結果不存在，請先執行 CalculatorNode")
            
            user_data = context["user_input"]
            metrics = context["metrics"]
            risks = "\n".join(context.get("risks", []))
            
            system_prompt = f"""
            你是一位年薪千萬的麥肯錫顧問，專門協助 CEO 制定年終獎金策略。
            
            【知識庫】：{BONUS_KB_TEXT}
            【企業數據】：營收 {user_data.get('revenue')} 萬，淨利 {user_data.get('net_profit')} 萬，風格 {user_data.get('style')}
            【計算結果】：總獎金池 {metrics.get('total_pool')} 元，人均 {metrics.get('per_head')} 元，平均 {metrics.get('months')} 個月
            【風險提示】：{risks}
            
            **你的任務**：用「黃金三段式」輸出，每段不超過 3 句話。不要說客套話。
            
            **輸出格式**（嚴格遵守）：
            
            ### 🎯 戰略判斷 (The Verdict)
            [一句話總結：目前的財務結構適合什麼策略？]
            
            ### ⚖️ 取捨分析 (The Trade-off)
            [明確指出：這個方案的風險是什麼？效益是什麼？老闆需要做什麼決定？]
            
            ### 💬 關鍵對話 (The Script)
            [只給一句話，針對最重要的員工群體（通常是 S 級）]
            """
            
            user_msg = "請根據上述數據，生成一份完整的年終獎金分配草案。"
        
        elif intent == "CHAT_FOLLOWUP":
            # 模式 B：回答單一問題（跳過計算，直接回答）
            user_data = context.get("user_input", {})
            metrics = context.get("metrics", {})
            risks = "\n".join(context.get("risks", []))
            
            # 聊天模式的 System Prompt 更簡潔，強調延續上下文
            system_prompt = f"""
            你是一位專業的年終獎金顧問，正在與企業主進行一對一諮詢。
            
            【知識庫】：{BONUS_KB_TEXT}
            【當前企業數據】：
            - 營收：{user_data.get('revenue', 'N/A')} 萬
            - 淨利：{user_data.get('net_profit', 'N/A')} 萬
            - 員工數：{user_data.get('employees', 'N/A')} 人
            - 平均月薪：{user_data.get('avg_salary', 'N/A')} 元
            - 管理風格：{user_data.get('style', 'N/A')}
            
            【已計算結果】：
            - 總獎金池：{metrics.get('total_pool', 'N/A')} 元
            - 人均金額：{metrics.get('per_head', 'N/A')} 元
            - 平均月數：{metrics.get('months', 'N/A')} 個月
            
            【已知風險】：{risks if risks else "無"}
            
            **你的任務**：根據用戶的問題，提供具體、可執行的建議。回答要簡潔、直接，不要重複已經說過的內容。
            """
            
            user_msg = context.get("latest_user_question", "")
            
            if not user_msg:
                raise ValueError("聊天模式下必須提供 latest_user_question")
        
        # 呼叫 Gemini API
        from utils.gemini_client import call_gemini_logic
        
        history = context.get("history", [])
        response = call_gemini_logic(system_prompt, user_msg, history)
        
        # 存回 Context
        context["ai_response"] = response
        context["system_prompt"] = system_prompt  # 用於 Debug
        
        return context
```

💡 **關鍵設計要點**：

1. **狀態管理**：使用 `st.session_state.messages` 維護對話歷史
2. **意圖分離**：聊天時只執行 AdvisorNode，不重新計算
3. **上下文保持**：聊天時使用已存在的 `pipeline_context`，確保 AI 知道企業數據
4. **快捷按鈕**：提供常見問題的快速入口，提升用戶體驗
5. **錯誤處理**：如果用戶還沒生成報告就聊天，友善提示先執行計算
4. 異常處理與防呆 (Safety Nets)
為了避免老闆在使用時看到紅色的 Python Error Traceback，我們需要三層防護網。

🛡️ 防護規格：

第一層：API Key 檢查 (App Start) 在 main.py 一開始就檢查：

```python
if not get_api_key():
    st.error("⛔ 未偵測到 Gemini API Key。請設定 .env 或 Streamlit Secrets。")
    st.stop() # 直接停止執行，不讓後面程式碼跑
```
第二層：數學除零保護 (Calculator Node) 在 calculator.py 中：

Python

if data["employees"] == 0:
    st.warning("員工人數為 0，無法計算人均獎金。")
    # 回傳預設值，讓 Pipeline 繼續跑，但不崩潰
    context["metrics"] = {"per_head": 0, "months": 0} 
    return context 
第三層：超時與重試 (User Action) Gemini API 偶爾會 timeout。我們在呼叫 Pipeline 時加上 try-except：

Python

# main.py
if start_btn:
    with st.spinner("AI 大腦運算中..."):
        try:
            result = pipeline.run(context)
        except Exception as e:
            st.error(f"系統暫時繁忙，請稍後重試。錯誤代碼：{e}")
            # 這裡可以加一個 st.button("重試")

第七章：🚨 三大 Debug 風險預警與開發前必備清單 (Critical Risks & Pre-coding Checklist)

🚨 第一部分：三大 Debug 風險預警 (Critical Risks)

1. Streamlit 的「狀態重置」陷阱 (The Rerun Trap)

風險描述： Streamlit 的機制是「只要有任何元件互動（例如輸入聊天訊息），整個 Python Script 就會從頭跑到尾」。

場景模擬：

用戶填完數據，點擊「生成草案」。Pipeline 跑完，算出獎金池 50 萬。

用戶在下方聊天框輸入：「如果不發給新人會怎樣？」

Crash 點： 當用戶按下 Enter，Streamlit 重新執行。如果你的程式碼沒有把 context 存進 st.session_state，這時候 Pipeline 會重置，導致 context 變回空值或初始值。AI 會回答：「抱歉，我不知道您的獎金池是多少。」

解決方案：

必須確保 context 物件是持久化的。

修正準備： 在 main.py 必須有一段邏輯是 `if "context" not in st.session_state: st.session_state.context = {}`。

📄 程式碼規格 (main.py 狀態初始化)：

```python
# [Snippet] 用於 main.py 的狀態管理
if "pipeline_context" not in st.session_state:
    st.session_state.pipeline_context = {}  # 用來存計算結果
if "messages" not in st.session_state:
    st.session_state.messages = []          # 用來存對話歷史

# 定義一個回調函數，當數據改變時清空緩存
def reset_on_change():
    st.session_state.pipeline_context = {}
    st.session_state.messages = []
    # 這裡可以加 toast 提示用戶
```

然後在每個 `st.number_input` 加上 `on_change=reset_on_change`。

2. 「雙重觸發」導致的邏輯衝突 (Conflict of Intent)

風險描述： 我們只有一條 Pipeline，但有兩個觸發點（按鈕 vs. 聊天框）。

場景模擬：

按鈕意圖：GENERATE_FULL_REPORT（需要 Calculator + Scanner + Advisor）。

聊天意圖：CHAT_FOLLOWUP（只需要 Advisor，不需要重算數學）。

Crash 點： 如果我在聊天框打字，觸發了 Pipeline，結果 CalculatorNode 又跑了一次，甚至因為某些欄位被清空而報錯。

解決方案：

需要在 context 裡增加一個 `run_mode` 或 `intent` 標記。

AdvisorNode 需要寫 if 判斷：如果是 Follow-up，就不要重新寫整份報告，而是只回答問題。

📄 程式碼規格 (nodes/advisor.py 意圖判斷)：

```python
class AdvisorNode(BaseNode):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        intent = context.get("current_intent", "GENERATE_REPORT")
        
        if intent == "GENERATE_REPORT":
            # 模式 A：生成完整報告（需要完整 Pipeline）
            # 確保 CalculatorNode 已執行（精實方案：風險檢查已合併）
            if "metrics" not in context:
                raise ValueError("計算結果不存在，請先執行 CalculatorNode")
            user_msg = "請根據上述數據，生成一份完整的年終獎金分配草案。"
        
        elif intent == "CHAT_FOLLOWUP":
            # 模式 B：回答單一問題（跳過計算，直接回答）
            user_msg = context.get("latest_user_question", "")
            # 使用已存在的 context["metrics"] 和 context["risks"]
            # 不需要重新計算
        
        # 呼叫 Gemini API
        from utils.gemini_client import call_gemini_logic
        response = call_gemini_logic(system_prompt, user_msg, context.get("history", []))
        
        context["ai_response"] = response
        return context
```

3. 數學運算的邊界值 (ZeroDivisionError)

風險描述： 雖然我們擋了「員工數不為0」，但漏了其他分母。

場景模擬：

用戶手滑，把「平均月薪」填成 0 或刪除成空值。

公式 `months = per_head / data["avg_salary"]` 立即崩潰。

解決方案：

CalculatorNode 必須加強防呆，或者 Streamlit 的 `number_input` 必須設定 `min_value=1`（不能是 0）。

📄 程式碼規格 (nodes/calculator.py 加強版)：

```python
class CalculatorNode(BaseNode):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        data = context["user_input"]
        
        # 1. 安全檢查：避免除以零的錯誤 (Edge Case)
        if data["employees"] <= 0:
            raise ValueError("員工人數不能為 0 或負數")
        
        if data["avg_salary"] <= 0:
            raise ValueError("平均月薪不能為 0 或負數")
        
        # 2. 核心公式
        pool = data["net_profit"] * (1 - data["retention_rate"])
        per_head = pool / data["employees"]
        months = per_head / data["avg_salary"]
        
        # 3. 寫入 Context
        context["metrics"] = {
            "total_pool": int(pool),
            "per_head": int(per_head),
            "months": round(months, 2)
        }
        
        return context
```

📄 程式碼規格 (main.py 輸入欄位防呆)：

```python
# 在 sidebar 中
avg_salary = st.number_input(
    "平均月薪 (元)", 
    value=40000,
    min_value=1,  # 關鍵：不能是 0
    step=1000
)

employees = st.number_input(
    "符合發放資格人數",
    value=5,
    min_value=1,  # 關鍵：不能是 0
    step=1
)
```

📋 第二部分：開發前必備清單 (Pre-coding Checklist)

在打開 VS Code 之前，請確認你桌上（或資料夾裡）已經準備好以下 4 樣東西：

1. .env 檔案 (機密鑰匙)

不要把 Key 寫在 Code 裡，這是工程師的鐵律。

檔案內容：

```plaintext
GEMINI_API_KEY=your-gemini-api-key-here
```

動作： 在專案根目錄建立此檔案。

⚠️ 注意： 絕對不要將 `.env` 檔案上傳到 GitHub。請確認 `.gitignore` 中包含 `.env`。

2. requirements.txt (依賴清單)

確保版本對齊，避免套件衝突。

檔案內容：

```plaintext
streamlit>=1.30.0
google-generativeai>=0.3.0
python-dotenv>=1.0.0
```

動作： 在專案根目錄建立此檔案，並執行 `pip install -r requirements.txt`。

3. 修正後的 main.py 狀態管理邏輯 (State Logic)

這是最關鍵的「膠水程式碼」。請把這段邏輯先準備好，貼在 main.py 的最上方：

```python
# [Snippet] 用於 main.py 的狀態管理
if "pipeline_context" not in st.session_state:
    st.session_state.pipeline_context = {}  # 用來存計算結果
if "messages" not in st.session_state:
    st.session_state.messages = []          # 用來存對話歷史

# 定義一個回調函數，當數據改變時清空緩存
def reset_on_change():
    """
    流程顧問原則：數據變動時必須清空所有緩存，並標記數據已變動。
    這樣可以強迫用戶重新生成報告，確保決策基於最新數據。
    """
    st.session_state.pipeline_context = {}  # 清空 Pipeline 結果
    st.session_state.messages = []  # 清空對話歷史
    st.session_state.data_changed = True  # ⚠️ 關鍵：標記數據已變動
    # 注意：toast 在回調函數中可能不會顯示，所以我們在 check_reset_condition 中處理
```

然後在每個 `st.number_input` 和 `st.slider` 加上 `on_change=reset_on_change`：

```python
# 範例：在 sidebar 中
revenue = st.number_input(
    "年度總營收 (萬元)", 
    value=1000, 
    step=10,
    on_change=reset_on_change  # ⚠️ 關鍵：數據變動時觸發
)

retention = st.slider(
    "公司安全氣囊 (%)",
    min_value=0,
    max_value=100,
    value=70,
    on_change=reset_on_change  # ⚠️ 關鍵：數據變動時觸發
)
```

4. 真實的 Gemini API Wrapper (Tools)

PDR 給的是模擬數據，你需要一個真的能跑的函數。建議建立 `utils/gemini_client.py`：

```python
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
```

然後在 `nodes/advisor.py` 中：

```python
from utils.gemini_client import call_gemini_logic

# 在 AdvisorNode.execute() 中使用
response = call_gemini_logic(system_prompt, user_msg, history, model="gemini-2.0-flash-exp", temperature=0.7)
```

🛠️ 第三部分：嚴格工程師的最終建議 (The Final Verdict)

Jack，你的設計 90% 是完美的。

那 10% 的風險在於：**你把 Streamlit 當成標準網頁開發了。 Streamlit 不是 React，它沒有複雜的 State Hook，它只有「一直重跑」。**

關鍵認知轉換：

1. **狀態即生命**：所有需要「記住」的東西，都必須存在 `st.session_state`。不要用全域變數，不要用類別屬性（除非用 `@st.cache_resource`）。

2. **意圖分離**：按鈕點擊和聊天輸入是兩種不同的「意圖」，必須在 context 中明確標記，讓 Pipeline 知道該執行哪些節點。

3. **防呆優先**：在寫業務邏輯之前，先把所有 `number_input` 的 `min_value` 設好，把所有可能的除以零場景都擋掉。

4. **測試驅動**：寫完每個 Node 後，立刻測試邊界值（0、負數、超大數），不要等到整合測試才發現。

最後提醒： 當你看到 `NameError: name 'context' is not defined` 或 `KeyError: 'metrics'` 時，99% 的機率是狀態管理沒做好。回頭檢查 `st.session_state` 的初始化邏輯。

第八章：產品升級策略：從算帳工具到決策引擎 (From Calculator to Decision Engine)

🎯 核心問題診斷

以「管理顧問 (MBB Level Consulting)」的標準來看，目前只有及格 (60分)。

為什麼？因為它還停留在「算帳工具 (Calculator)」的層次，而沒有達到「決策引擎 (Decision Engine)」的高度。

要在不增加文字的前提下提升水準，程式碼不需要變多，而是需要注入「顧問的靈魂」。

以下針對三個維度，提出「精實 (Lean) 與升級 (Elevate)」的修改建議，讓產品從 HR 行政工具，變身為 CEO 的策略幕僚。

一、視角昇華：從「填數字」轉為「調槓桿」

目前的介面像是在「報稅」，老闆填得很痛苦。頂級顧問會告訴老闆：「你只需要關注三個槓桿。」

🔥 修改策略：UI 重新分組 (Re-grouping)

不要只列出一堆欄位，將側邊欄改為「CEO 的三大決策槓桿」：

**生存槓桿 (Survival Lever)**：

- 原欄位：保留盈餘 %
- 顧問化重命名：「公司安全氣囊 (Safety Margin)」
- 精實話術：滑動時，直接顯示「這筆錢能讓公司如果不賺錢活 X 個月」

📄 程式碼規格 (main.py sidebar 改寫)：

```python
with st.sidebar:
    st.title("🎯 CEO 決策槓桿")
    
    # 槓桿 1：生存槓桿
    st.subheader("🛡️ 生存槓桿 (Safety Margin)")
    retention = st.slider(
        "公司安全氣囊 (%)",
        min_value=0,
        max_value=100,
        value=70,
        help="這筆保留盈餘能讓公司在零收入狀態下存活幾個月？"
    )
    
    # 動態計算並顯示存活月數
    if "metrics" in st.session_state.pipeline_context:
        monthly_burn = st.session_state.pipeline_context.get("monthly_burn", 0)
        survival_months = (retention / 100.0 * net_profit) / monthly_burn if monthly_burn > 0 else 0
        st.caption(f"💡 這筆錢能讓公司存活約 {survival_months:.1f} 個月")
    
    st.markdown("---")
    
    # 槓桿 2：激勵槓桿
    st.subheader("🚀 激勵槓桿 (Motivation Strategy)")
    style = st.radio(
        "人才投資策略",
        options=["留才優先 (Retention First)", "戰功優先 (Performance First)", "團隊優先 (Team First)"],
        help="這決定了獎金池的分配邏輯"
    )
    
    st.markdown("---")
    
    # 槓桿 3：現實槓桿
    st.subheader("💰 現實槓桿 (Financial Reality)")
    st.caption("請輸入公司的財務底氣")
    revenue = st.number_input("年度總營收 (萬元)", value=1000, step=10)
    net_profit = st.number_input("稅前淨利 (萬元)", value=100, step=10)
    employees = st.number_input("符合發放資格人數", value=5, min_value=1)
    avg_salary = st.number_input("平均月薪 (元)", value=40000, min_value=1, step=1000)
```

💡 價值提升點： 老闆不是在「填表」，而是在「制定戰略」。

二、輸出昇華：從「分配草案」轉為「決策備忘錄」

目前的 AI 輸出是「給你看結果」。頂級顧問的輸出是「逼你做決定」。

🔥 修改策略：AI 回答結構 (Insight over Info)

請修改 AdvisorNode 的 Prompt，強迫 AI 只輸出「黃金三段式」，刪除所有廢話：

**The Verdict (戰略判斷)**：

- Bad: "根據計算，平均發放 1.5 個月..."
- Good: "目前的獲利結構健康，具備『積極搶才』的本錢。建議發放水準設定為『市場前 25%』以建立雇主品牌。"

**The Trade-off (取捨分析)**：

- Bad: "S級發 2 個月，A級發 1.5 個月..."
- Good: "本方案將 60% 獎金集中於前 20% 員工。風險是可能造成後段班不安，但效益是確保核心戰力明年 Q1 不流失。您是否接受此風險？"

**The Script (關鍵對話)**：

- 只給一句話。
- Good: "對 S 級員工的關鍵一句話：『這筆獎金不是獎勵過去，而是我對你明年帶領新專案的投資。』"

📄 程式碼規格 (nodes/advisor.py System Prompt 升級)：

```python
class AdvisorNode(BaseNode):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # ... 組合知識庫和數據 ...
        
        system_prompt = f"""
        你是一位年薪千萬的麥肯錫顧問，專門協助 CEO 制定年終獎金策略。
        
        【知識庫】：{BONUS_KB_TEXT}
        【企業數據】：{user_data}
        【計算結果】：{metrics}
        【風險提示】：{risks}
        
        **你的任務**：用「黃金三段式」輸出，每段不超過 3 句話。不要說客套話。
        
        **輸出格式**（嚴格遵守）：
        
        ### 🎯 戰略判斷 (The Verdict)
        [一句話總結：目前的財務結構適合什麼策略？]
        
        ### ⚖️ 取捨分析 (The Trade-off)
        [明確指出：這個方案的風險是什麼？效益是什麼？老闆需要做什麼決定？]
        
        ### 💬 關鍵對話 (The Script)
        [只給一句話，針對最重要的員工群體（通常是 S 級）]
        
        **禁止事項**：
        - 不要列出所有等級的獎金數字（那是計算器的活）
        - 不要說「根據計算...」（直接給判斷）
        - 不要超過一頁 A4 紙的長度
        """
        
        # ... 呼叫 Gemini API ...
        return context
```

💡 價值提升點： 顧問的價值不在於算得準，而在於幫老闆「看清代價 (Trade-off)」。

三、靈魂昇華：知識庫的「觀點化」

目前的 KB 是「教科書」。頂級顧問賣的是「觀點 (Point of View)」。

🔥 修改策略：注入「反直覺」的洞察

請在你的 knowledge.py 中，加入這三條「刺人」的規則，讓 AI 講出老闆不敢講的話：

**「沒有驚喜，就沒有激勵」**：

如果算出來跟去年一樣，AI 必須警告：「發放金額與去年持平，這在員工心理帳戶等於『沒漲』。建議撥出 10% 預算設立『特殊名目獎金』創造驚喜。」

**「不發錢也是一種策略」**：

對於 C 級員工，AI 必須直言：「給 C 級員工 0.5 個月是浪費資源。建議給 0，並將面談轉為『留職停薪』或『轉崗』的談判。」

**「老闆的恐懼」**：

AI 主動偵測：「您保留了 90% 盈餘，數據顯示這源於對明年的不安全感。但過度防禦會導致團隊『縮手縮腳』。建議釋放 5% 作為『試錯基金』。」

📄 程式碼規格 (assets/knowledge.py 新增章節)：

請參考 KB.md 第六章的內容，將這些「反直覺洞察」加入知識庫。

🚀 總結：如何做到「精實而有水準」？

要在不增加文字的前提下提升水準，程式碼不需要變多，而是 Prompt 要變「兇」一點。

**具體行動**：

1. **UI 層**： 改標籤名稱，用「商業詞彙」取代「會計詞彙」。
2. **AI 層**： 修改 System Prompt，加上一句指令：「請扮演一位年薪千萬的麥肯錫顧問，講話簡潔、直接、並指出決策的代價。不要說客套話。」
3. **結果層**： 輸出的 Markdown 只要一頁 (One-pager)，不要長篇大論。

這就是 High-Level Consulting：話少，但句句見血。

---

第九章：配置中心使用指南 (Configuration Center Guide)

💡 **設計理念**：將所有可調整的內容（知識庫、表單欄位、快捷問題、提示詞）集中管理，不需要在程式碼中到處搜尋。

### 📝 修改指南

#### 1. 修改知識庫內容
**檔案位置**：`assets/knowledge.py`

**修改內容**：編輯 `BONUS_KB_TEXT` 變數中的文字內容

**範例**：
```python
# assets/knowledge.py
BONUS_KB_TEXT = """
# 年終獎金發放顧問知識庫

## 第一章：核心哲學
...（在這裡修改知識庫內容）...
"""
```

#### 2. 修改表單欄位
**檔案位置**：`config/settings.py`

**修改內容**：編輯 `FORM_FIELDS` 字典

**範例**：
```python
# config/settings.py
FORM_FIELDS = {
    "revenue": {
        "label": "年度總營收 (萬元)",  # 修改這裡改變顯示文字
        "default": 1000,              # 修改這裡改變預設值
        "step": 10,
        "help": None
    },
    # ... 其他欄位
}
```

#### 3. 修改快捷按鈕問題
**檔案位置**：`config/settings.py`

**修改內容**：編輯 `QUICK_QUESTIONS` 字典

**範例**：
```python
# config/settings.py
QUICK_QUESTIONS = {
    "analyze_risks": {
        "label": "⚠️ 分析潛在風險",  # 修改按鈕顯示文字
        "question": "請詳細分析這個方案的潛在風險..."  # 修改問題內容
    },
    # ... 其他問題
}
```

#### 4. 修改提示詞模板
**檔案位置**：`config/settings.py`

**修改內容**：編輯 `PROMPT_TEMPLATES` 字典

**範例**：
```python
# config/settings.py
PROMPT_TEMPLATES = {
    "generate_report": """
你是一位年薪千萬的麥肯錫顧問...
...（在這裡修改提示詞內容）...
""",
    # ... 其他模板
}
```

### 🎯 配置中心的優勢

1. **集中管理**：所有可調整內容在一個檔案，不需要在程式碼中搜尋
2. **易於修改**：改表單欄位、快捷問題、提示詞，只需要改 `config/settings.py`
3. **版本控制友好**：配置變更的歷史清晰可見
4. **擴展性強**：未來新增欄位或問題，只需在配置中心添加

### ⚠️ 注意事項

- **知識庫內容**：修改 `assets/knowledge.py` 中的 `BONUS_KB_TEXT`
- **表單和問題**：修改 `config/settings.py` 中的對應字典
- **不要修改程式碼邏輯**：只需要修改配置檔案，不需要動 `main.py` 或 `nodes/` 中的程式碼
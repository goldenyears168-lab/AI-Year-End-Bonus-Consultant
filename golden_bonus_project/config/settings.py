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


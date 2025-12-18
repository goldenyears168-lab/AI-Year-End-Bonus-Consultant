# nodes/advisor.py
from core.base_node import BaseNode
from config.settings import PROMPT_TEMPLATES  # 從配置中心讀取提示詞模板
from assets.knowledge import BONUS_KB_TEXT
from typing import Dict, Any

def _needs_human_escalation(question: str, response: str) -> tuple[bool, str]:
    """
    最小保守判斷：若問題可能涉及法規/稅務/勞資等高風險領域，或模型回覆明顯拒答/空泛，
    則建議諮詢真人專業顧問。回傳 (是否需要, 建議諮詢方向文字)。
    """
    q = (question or "").replace(" ", "")
    r = (response or "")

    # 1) 明顯拒答/空泛
    refusal_markers = [
        "抱歉，我無法回答", "我無法回答", "不能回答", "無法提供", "我不知道",
        "無法判斷", "不確定", "資訊不足", "超出我的範圍",
    ]
    if any(m in r for m in refusal_markers):
        return (True, "目前回覆有限，建議補充資訊或諮詢真人專業以避免誤判。")

    # 2) 高風險/專業領域關鍵字（先回答能回答的，再建議詢問）
    pro_keywords = {
        "law_hr": ["勞基法", "勞資", "解雇", "資遣", "加班", "工時", "特休", "最低工資", "勞健保", "勞退"],
        "tax_accounting": ["稅", "扣繳", "申報", "所得稅", "營所稅", "二代健保", "費用化", "分錄", "審計", "財報"],
        "legal": ["契約", "合約", "法務", "訴訟", "違法", "合規"],
        "comp": ["薪酬制度", "股票", "期權", "ESOP", "分紅", "獎酬"],
    }
    if any(k in q for ks in pro_keywords.values() for k in ks):
        return (True, "此題牽涉法規/稅務/勞資或薪酬制度細節，建議由真人專業顧問確認。")

    return (False, "")

def _contains_questions(text: str) -> bool:
    """
    偵測回覆是否包含反問/問句特徵（保守判斷）。
    """
    t = (text or "")
    if not t:
        return False
    markers = ["？", "?", "請問", "能否", "可以提供", "可否", "方便提供"]
    return any(m in t for m in markers)

def _looks_like_report_payload(text: str) -> bool:
    """
    嚴格判斷：只有當輸入明顯是「結構化公司資料貼文」時才進入「原理解讀模式」。
    注意：使用者可能不會帶 report: 開頭，可能直接從 company:/financials: 開始。
    """
    t = (text or "").lower()
    # 嚴格：至少出現 company: 且同時出現 1 個以上常見區塊（financials/bonus/departments/growthEngine/warnings/recommendations）
    has_company_block = "company" in t
    other_blocks = [
        "financials",
        "bonus",
        "departments",
        "growthengine",
        "warnings",
        "recommendations",
    ]
    has_any_other = any(b in t for b in other_blocks)
    return has_company_block and has_any_other

def _remove_questions(text: str) -> str:
    """
    最小保守修正：移除含問句標點的行，並把常見反問句型替換成「下一步建議」陳述句。
    目標是保證 UI 不出現反問，而不是做完美語言改寫。
    """
    if not text:
        return text

    lines = text.splitlines()
    kept: list[str] = []
    for line in lines:
        if "？" in line or "?" in line:
            continue
        kept.append(line)

    cleaned = "\n".join(kept).strip()
    # 額外處理：若殘留「請問/能否」等但不含問號，改寫成指令式下一步
    cleaned = cleaned.replace("請問", "下一步建議：")
    cleaned = cleaned.replace("能否", "下一步建議：")
    cleaned = cleaned.replace("可否", "下一步建議：")
    cleaned = cleaned.replace("可以提供", "下一步建議：提供")
    cleaned = cleaned.replace("方便提供", "下一步建議：提供")
    return cleaned

def _strip_internal_refs(text: str) -> str:
    """
    保底清理：移除知識庫內部代碼（C_XXXX / R_XXXX 等）。
    """
    if not text:
        return text

    lines = text.splitlines()
    out: list[str] = []
    for line in lines:
        if "C_" in line or "R_" in line:
            # 移除包含內部代碼的整行（避免露出 chunk id/規則代碼）
            continue
        out.append(line)
    return "\n".join(out).strip()

def _ensure_followup_format(text: str) -> str:
    """
    最小保守保底：確保 followup 模式輸出包含四個標題：
    ### 原理總覽 / ### 這份報告如何推導 / ### 如何解讀這份結果 / ### 還可以回答的問題

    原則：不再額外呼叫模型；只在缺少標題時補上框架，避免 UI/使用者體感「格式不穩」。
    """
    if not text:
        return (
            "### 原理總覽\n（內容暫缺）\n\n"
            "### 這份報告如何推導\n（內容暫缺）\n\n"
            "### 如何解讀這份結果\n（內容暫缺）\n\n"
            "### 還可以回答的問題\n"
            "- 階段判斷的邏輯與門檻解讀\n"
            "- HR Ratio 的意義、風險區間、以及為什麼只用於風險而不決定階段\n"
            "- 增長引擎如何映射到部門權重（解讀分配理由）\n"
        )

    required_markers = [
        "### 原理總覽",
        "### 這份報告如何推導",
        "### 如何解讀這份結果",
        "### 還可以回答的問題",
    ]
    if all(m in text for m in required_markers):
        return text

    # 若模型沒有依格式輸出：用最小包裝補齊標題，並把原文放進「解讀」段落避免資訊流失
    body = (text or "").strip()
    return (
        "### 原理總覽\n"
        "這份回覆主要用「階段 / 用人成本風險 / 增長引擎與部門權重」三個概念，來解釋年終獎金的結構性取捨。\n\n"
        "### 這份報告如何推導\n"
        "- 階段判斷：用營收與毛利看養人能力與現金流承受度，決定偏向保留或激勵的框架位置。\n"
        "- HR Ratio：用人事成本占毛利看用人成本風險，作為風險解讀而非直接決定階段。\n"
        "- 增長引擎與權重：用增長方式映射到部門的相對權重，解釋資源傾斜的理由。\n\n"
        "### 如何解讀這份結果\n"
        f"{body}\n\n"
        "### 還可以回答的問題\n"
        "- 階段判斷的邏輯與門檻解讀\n"
        "- HR Ratio 的意義、風險區間、以及為什麼只用於風險而不決定階段\n"
        "- 獎金池為何在不同階段會偏向季度或年底（解讀結構而非建議）\n"
        "- 增長引擎如何映射到部門權重（解讀分配理由）\n"
    )

class AdvisorNode(BaseNode):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        intent = context.get("current_intent", "CHAT")
        user_data = context.get("user_input", {})
        metrics = context.get("metrics", {})
        risks = "\n".join(context.get("risks", []))
        company_context_text = (context.get("company_context_text") or "").strip()
        company_context_block = ""
        if company_context_text:
            company_context_block = f"\n\n【企業補充資訊】\n{company_context_text}\n"

        # 針對「自我介紹/怎麼用」類問題做保守處理：避免被模型安全策略誤判而拒答
        latest_q = (context.get("latest_user_question") or "").strip()
        if intent == "CHAT" and latest_q:
            q_norm = latest_q.replace(" ", "")
            intro_triggers = [
                "你是誰", "你是什麼", "你能做什麼", "你可以做什麼",
                "怎麼用", "如何使用", "使用方法", "你會什麼",
            ]
            if any(t in q_norm for t in intro_triggers):
                context["ai_response"] = (
                    "我是 WinLeaders-Bonus 年終獎金顧問。"
                    "我可以協助你制定年終獎金策略、評估風險、以及把獎金發放邏輯講清楚。"
                    "下一步你可以直接貼上公司報告（stage/revenue/grossMargin/hrRatio/bonus pool/部門分配/增長引擎），我會用同一套框架幫你做策略判斷與可執行建議。"
                )
                context["system_prompt"] = "local_intro_fallback"
                return context

            # 若是「覺得太少/不滿意/想更詳細」等 follow-up 型問題，改用 followup 模板產出更顧問式內容
            followup_triggers = [
                "不滿意", "太少", "不夠", "更詳細", "詳細說明", "詳細解釋",
                "說明一下", "再多一點", "多一點", "具體一點", "更具體", "怎麼調整",
                "為什麼", "原因", "取捨", "方案",
            ]
            if any(t in q_norm for t in followup_triggers):
                intent = "CHAT_FOLLOWUP"

            # 若使用者貼的是 report 結構化資料，走「原理解讀」模式
            if _looks_like_report_payload(latest_q):
                intent = "CHAT_FOLLOWUP"

            # 若已載入企業補充資訊，且使用者在問「解說/原理/解讀」類問題，優先走原理解讀模式
            if company_context_text:
                explain_triggers = ["解說", "原理", "解讀", "推導", "介紹", "怎麼看", "如何看"]
                if any(t in q_norm for t in explain_triggers):
                    intent = "CHAT_FOLLOWUP"
        
        if intent == "GENERATE_REPORT":
            # 使用配置中心的提示詞模板
            system_prompt = PROMPT_TEMPLATES["generate_report"].format(
                knowledge_base=BONUS_KB_TEXT,
                net_profit=user_data.get('net_profit', 'N/A'),
                style=user_data.get('style', 'N/A'),
                total_pool=metrics.get('total_pool', 'N/A'),
                per_head=metrics.get('per_head', 'N/A'),
                months=metrics.get('months', 'N/A'),
                risks=risks if risks else "無"
            ) + company_context_block
            user_msg = "請根據上述數據，生成一份完整的年終獎金分配草案。"
        
        elif intent == "CHAT_FOLLOWUP":
            # 使用配置中心的聊天提示詞模板
            system_prompt = PROMPT_TEMPLATES["chat_followup"].format(
                knowledge_base=BONUS_KB_TEXT,
                net_profit=user_data.get('net_profit', 'N/A'),
                employees=user_data.get('employees', 'N/A'),
                avg_salary=user_data.get('avg_salary', 'N/A'),
                style=user_data.get('style', 'N/A'),
                total_pool=metrics.get('total_pool', 'N/A'),
                per_head=metrics.get('per_head', 'N/A'),
                months=metrics.get('months', 'N/A'),
                risks=risks if risks else "無"
            ) + company_context_block
            user_msg = context.get("latest_user_question", "")
        
        elif intent == "CHAT":
            # 純對話模式：走顧問建議模板（仍不反問、不用問號）
            system_prompt = PROMPT_TEMPLATES.get("chat_advice", PROMPT_TEMPLATES["chat"]).format(
                knowledge_base=BONUS_KB_TEXT
            ) + company_context_block
            user_msg = context.get("latest_user_question", "")
        
        # 呼叫 Gemini API
        from utils.gemini_client import call_gemini_logic
        history = context.get("history", [])
        response = call_gemini_logic(system_prompt, user_msg, history)

        # 精實化：只呼叫模型一次；其餘用本地後處理做保底（降低延遲/成本/不確定性）
        response = _strip_internal_refs(response)
        if _contains_questions(response):
            response = _remove_questions(response)
        if intent == "CHAT_FOLLOWUP":
            response = _ensure_followup_format(response)

        # 若看起來超出知識庫/專業高風險領域：先保留既有回答，再補上「建議諮詢真人」提示
        need_escalation, escalation_note = _needs_human_escalation(latest_q, response)
        if need_escalation:
            response = (
                (response or "").rstrip()
                + "\n\n"
                + "### 建議諮詢真人專業\n"
                + f"- {escalation_note}\n"
                + "- 若涉及稅務/扣繳/費用化：建議詢問會計師或稅務顧問（帶上薪資結構、獎金發放規則、員工清冊）。\n"
                + "- 若涉及勞資/工時/加班/勞退勞健保：建議詢問勞資顧問或律師（帶上勞動契約、出勤/加班制度、薪資項目）。\n"
                + "- 若涉及制度設計與留才：建議詢問薪酬顧問（帶上績效制度、職等/職族、過往流動率與關鍵人才名單）。\n"
            )
        
        context["ai_response"] = response
        context.setdefault("system_prompt", system_prompt)
        
        return context


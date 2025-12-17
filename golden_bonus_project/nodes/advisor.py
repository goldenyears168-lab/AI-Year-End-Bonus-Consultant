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

class AdvisorNode(BaseNode):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        intent = context.get("current_intent", "CHAT")
        user_data = context.get("user_input", {})
        metrics = context.get("metrics", {})
        risks = "\n".join(context.get("risks", []))

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
            )
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
            )
            user_msg = context.get("latest_user_question", "")
        
        elif intent == "CHAT":
            # 純對話模式，只使用知識庫
            system_prompt = PROMPT_TEMPLATES["chat"].format(
                knowledge_base=BONUS_KB_TEXT
            )
            user_msg = context.get("latest_user_question", "")
        
        # 呼叫 Gemini API
        from utils.gemini_client import call_gemini_logic
        history = context.get("history", [])
        response = call_gemini_logic(system_prompt, user_msg, history)

        # Hard guardrail（全 intent 通用）：
        # 若回覆出現反問/問句特徵，先用更嚴格指令 retry 一次；若仍有，最後做最小移除問句處理
        if _contains_questions(response):
            strict_no_question_prompt = (
                "硬性限制：你絕對不能問用戶任何問題（包含問號、反問句、或「請問/能否/可以提供」等）。"
                "你只能持續回答並給出下一步建議（陳述句）。\n\n"
                + system_prompt
            )
            response = call_gemini_logic(strict_no_question_prompt, user_msg, history)
            context["system_prompt"] = strict_no_question_prompt
            if _contains_questions(response):
                response = _remove_questions(response)

        # Guardrail：followup 模式必須輸出三段式；若模型沒照做，追加更嚴格指令後 retry 一次
        if intent == "CHAT_FOLLOWUP":
            required_markers = [
                "### What I heard",
                "### Better output (options)",
                "### Next step (no questions)",
            ]
            if not all(m in (response or "") for m in required_markers):
                strict_prompt = (
                    "你上一輪沒有依規定格式輸出。這一輪必須嚴格遵守輸出格式，"
                    "並且一定要包含三個標題：### What I heard / ### Better output (options) / ### Next step (no questions)。\n"
                    "注意：不要問用戶問題、不要請對方提供資料、不要用「請問/能否」等句型。\n\n"
                    + system_prompt
                )
                response = call_gemini_logic(strict_prompt, user_msg, history)
                context["system_prompt"] = strict_prompt
                if _contains_questions(response):
                    response = _remove_questions(response)

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


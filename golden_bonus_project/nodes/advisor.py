# nodes/advisor.py
from core.base_node import BaseNode
from config.settings import PROMPT_TEMPLATES  # 從配置中心讀取提示詞模板
from assets.knowledge import BONUS_KB_TEXT
from typing import Dict, Any

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
                    "你可以先告訴我：公司淨利/員工數/平均月薪/想走留才或激勵，我再給你建議。"
                )
                context["system_prompt"] = "local_intro_fallback"
                return context
        
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
        
        context["ai_response"] = response
        context["system_prompt"] = system_prompt
        
        return context

